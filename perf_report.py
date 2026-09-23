"""One ordered event pass; preserves baseline populations with stable score summation."""
from collections import defaultdict
import math


def _run(con,date_from='2026-05-01',date_to='2026-06-30'):
    con.row_factory=None
    tenants=dict(con.execute('SELECT tenant_id,plan FROM tenant'))
    lines={};groups={}
    customers=defaultdict(set)
    for lid,tenant,customer,channel,created in con.execute('SELECT line_id,tenant_id,customer_id,channel,created_at FROM order_line'):
        day=created[:10];key=(tenant,channel,day)
        lines[lid]=(tenant,channel,day)
        customers[key].add(customer)
        if date_from<=day<=date_to and tenant in tenants:
            if key not in groups:groups[key]=set()
            groups[key].add(lid)
    disabled={(t,c) for t,c in con.execute('SELECT tenant_id,item_code FROM item WHERE disabled=1')}
    accepted=defaultdict(set);considered=defaultdict(int)
    scores=defaultdict(list);latencies=defaultdict(list)
    items=defaultdict(set);disabled_count=defaultdict(int)
    # INTEGER PRIMARY KEY order matches original table scans, including AVG addition order.
    for tenant,lid,code,score,ok,latency,created in con.execute('SELECT tenant_id,line_id,item_code,score,accepted,latency_ms,created_at FROM match_event ORDER BY event_id'):
        day=created[:10];td=(tenant,day)
        if lid in lines:
            lt,channel,lday=lines[lid]
            considered[(lt,channel,lday)]+=1
            if ok==1:accepted[(tenant,channel,lday)].add(lid)
        items[td].add(code)
        if latency is not None:latencies[td].append(latency)
        if ok==1:
            if score is not None:scores[td].append(score)
            if (tenant,code) in disabled:disabled_count[td]+=1
    day_metrics={}
    for tenant,day in items:
        td=(tenant,day);ls=latencies[td];total=sum(ls);n=len(ls)
        previous=con.execute("SELECT date(?,'-1 day')",(day,)).fetchone()[0]
        ordered=sorted(ls)
        day_metrics[td]=dict(avg_accept_score=math.fsum(scores[td])/len(scores[td]) if scores[td] else None,
            max_latency_ms=max(ls) if ls else None,avg_latency_ms=total/n if n else None,
            repeat_items_prev_day=len(items[td]&items.get((tenant,previous),set())),
            accepted_disabled=disabled_count[td],p95_latency_ms=ordered[math.ceil(.95*n)-1] if n else None)
    out=[]
    for (tenant,channel,day),ids in sorted(groups.items()):
        row=dict(tenant_id=tenant,plan=tenants[tenant],channel=channel,day=day,lines_total=len(ids),
            lines_accepted=len(accepted[(tenant,channel,day)]),candidates_considered=considered[(tenant,channel,day)])
        row.update(day_metrics.get((tenant,day),dict(avg_accept_score=None,max_latency_ms=None,avg_latency_ms=None,repeat_items_prev_day=0,accepted_disabled=0,p95_latency_ms=None)))
        row['distinct_customers']=len(customers[(tenant,channel,day)])
        columns=('tenant_id','plan','channel','day','lines_total','lines_accepted','candidates_considered','avg_accept_score','max_latency_ms','avg_latency_ms','distinct_customers','repeat_items_prev_day','accepted_disabled','p95_latency_ms')
        out.append({k:row[k] for k in columns})
    return out


def run(con,date_from='2026-05-01',date_to='2026-06-30'):
    """Keep all passes in one snapshot without committing a caller's transaction."""
    owned=not con.in_transaction
    factory=con.row_factory
    if owned:con.execute('BEGIN')
    try:
        return _run(con,date_from,date_to)
    finally:
        con.row_factory=factory
        if owned:con.rollback()
