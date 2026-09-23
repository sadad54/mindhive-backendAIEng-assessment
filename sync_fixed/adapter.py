"""One SQLite file per tenant, durable outbox, bounded overlap pull, CAS-only push."""
import json,sqlite3,uuid
from datetime import datetime,timedelta,timezone
from starter.sync.fake_erp import ErpTimeout,ErpConflict

class PullCapacityError(RuntimeError):pass

def utc(remote_time):
    return datetime.strptime(remote_time,'%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone(timedelta(hours=8))).astimezone(timezone.utc).isoformat()

def canonical(payload):return json.dumps(payload,sort_keys=True,separators=(',',':'),allow_nan=False)

class Store:
    def __init__(self,path,tenant):
        self.db=sqlite3.connect(path)
        self.db.row_factory=sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL');self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT);
        CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY,payload TEXT NOT NULL,version INTEGER NOT NULL,updated_utc TEXT NOT NULL,dirty INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS applied(id TEXT,version INTEGER,PRIMARY KEY(id,version));
        CREATE TABLE IF NOT EXISTS outbox(op TEXT PRIMARY KEY,id TEXT NOT NULL,payload TEXT NOT NULL,base INTEGER NOT NULL,state TEXT NOT NULL,key TEXT NOT NULL UNIQUE);
        CREATE UNIQUE INDEX IF NOT EXISTS one_pending ON outbox(id) WHERE state IN ('pending','uncertain');
        CREATE TABLE IF NOT EXISTS conflicts(id TEXT PRIMARY KEY,remote TEXT NOT NULL,version INTEGER NOT NULL,reason TEXT NOT NULL);
        ''')
        with self.db:
            row=self.db.execute("SELECT value FROM meta WHERE key='tenant'").fetchone()
            if row and row[0]!=tenant:raise ValueError('Tenant store mismatch')
            self.db.execute("INSERT OR IGNORE INTO meta VALUES ('tenant',?)",(tenant,))
        self.tenant=tenant
    def close(self):self.db.close()
    def record(self,eid):
        r=self.db.execute('SELECT * FROM records WHERE id=?',(eid,)).fetchone()
        return dict(r) if r else None
    def cursor(self):
        r=self.db.execute("SELECT value FROM meta WHERE key='cursor'").fetchone();return r[0] if r else None
    def edit(self,eid,payload):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            if self.db.execute("SELECT 1 FROM outbox WHERE id=? AND state IN ('pending','uncertain')",(eid,)).fetchone():raise ValueError('Unresolved outbox operation; reconcile before editing')
            if self.db.execute('SELECT 1 FROM conflicts WHERE id=?',(eid,)).fetchone():raise ValueError('Manual conflict resolution required')
            r=self.record(eid)
            self.db.execute('INSERT OR REPLACE INTO records VALUES (?,?,?,?,1)',(eid,canonical(payload),r['version'] if r else 0,r['updated_utc'] if r else ''))
    def conflict(self,eid,remote,reason):
        self.db.execute('INSERT OR REPLACE INTO conflicts VALUES (?,?,?,?)',(eid,canonical(remote.payload) if remote else '{}',remote.version if remote else 0,reason))


def pull(erp,store,page_size=50,max_records=100000,full=False,crash_hook=None):
    if page_size<1 or max_records<page_size:raise ValueError('Invalid pull bounds')
    cursor=None if full else store.cursor()
    # ERP cursor stays in ERP local time; record timestamps are converted separately.
    since=(datetime.strptime(cursor,'%Y-%m-%d %H:%M:%S')-timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S') if cursor else None
    limit=page_size
    while True:
        page=erp.list_changes(since=since,limit=limit)
        if len(page)<limit:break
        if limit>=max_records:raise PullCapacityError('Cannot prove timestamp bucket drained; cursor unchanged')
        limit=min(max_records,limit*2)
    count=0
    with store.db:
        store.db.execute('BEGIN IMMEDIATE')
        for remote in page:
            local=store.record(remote.external_id)
            if local and local['dirty']:
                if remote.version!=local['version']:
                    pending=store.db.execute("SELECT * FROM outbox WHERE id=? AND state IN ('pending','uncertain')",(remote.external_id,)).fetchone()
                    own_result=(pending and remote.version==pending['base']+1 and canonical(remote.payload)==pending['payload'])
                    if not own_result:store.conflict(remote.external_id,remote,'remote_changed_while_dirty')
                continue
            if local and local['version']>=remote.version:continue
            store.db.execute('INSERT OR REPLACE INTO records VALUES (?,?,?,?,0)',(remote.external_id,canonical(remote.payload),remote.version,utc(remote.updated_at)))
            store.db.execute('INSERT OR IGNORE INTO applied VALUES (?,?)',(remote.external_id,remote.version));count+=1
            if crash_hook:crash_hook('after_record')
        if page:
            newest=max([r.updated_at for r in page]+([cursor] if cursor else []))
            store.db.execute("INSERT OR REPLACE INTO meta VALUES ('cursor',?)",(newest,))
        if crash_hook:crash_hook('before_commit')
    return count


def push(erp,store,max_attempts=3,crash_hook=None):
    if max_attempts<1:raise ValueError('max_attempts must be positive')
    with store.db:
        store.db.execute('BEGIN IMMEDIATE')
        for r in store.db.execute('SELECT * FROM records WHERE dirty=1').fetchall():
            if store.db.execute('SELECT 1 FROM conflicts WHERE id=?',(r['id'],)).fetchone():continue
            if store.db.execute("SELECT 1 FROM outbox WHERE id=? AND state IN ('pending','uncertain')",(r['id'],)).fetchone():continue
            op=uuid.uuid4().hex
            store.db.execute('INSERT INTO outbox VALUES (?,?,?,?,?,?)',(op,r['id'],r['payload'],r['version'],'pending',store.tenant+':'+op))
    if crash_hook:crash_hook('after_outbox_commit')
    pushed=0
    pending=store.db.execute("SELECT * FROM outbox WHERE state IN ('pending','uncertain') ORDER BY op").fetchall()
    for op in pending:
        # A durable conflict discovered by pull stops an already-pending operation too.
        if store.db.execute('SELECT 1 FROM conflicts WHERE id=?',(op['id'],)).fetchone():continue
        payload=json.loads(op['payload']);remote=None
        for _ in range(max_attempts):
            try:
                remote=erp.write(op['id'],payload,base_version=op['base'],idempotency_key=op['key'])
                break
            except ErpTimeout:
                with store.db:store.db.execute("UPDATE outbox SET state='uncertain' WHERE op=?",(op['op'],))
            except ErpConflict:
                current=erp.get(op['id'])
                # Expired key or crash: acknowledge desired state, never advance the CAS base.
                if current and current.version==op['base']+1 and canonical(current.payload)==op['payload']:
                    remote=current
                else:
                    with store.db:
                        store.conflict(op['id'],current,'compare_and_swap_conflict')
                        store.db.execute("UPDATE outbox SET state='conflict' WHERE op=?",(op['op'],))
                break
        if remote is None:continue
        if crash_hook:crash_hook('after_remote_commit')
        with store.db:
            store.db.execute('BEGIN IMMEDIATE')
            # edit() disallows concurrent mutation while this immutable operation is pending.
            store.db.execute('UPDATE records SET version=?,updated_utc=?,dirty=0 WHERE id=? AND payload=?',(remote.version,utc(remote.updated_at),op['id'],op['payload']))
            store.db.execute("UPDATE outbox SET state='done' WHERE op=?",(op['op'],))
            store.db.execute('INSERT OR IGNORE INTO applied VALUES (?,?)',(op['id'],remote.version))
        pushed+=1
    return pushed
