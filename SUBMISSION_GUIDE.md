# Submission guide — the steps Sadad must do

The code, predictions, analysis and documentation are prepared. This guide covers the remaining personal checks and submission. Do not describe host measurements as laptop measurements until you run them yourself. Do not claim the AI-authored code was unaided work; attribution is already in README.md.

## 1. Check the deadline and submission channel (2 minutes)
Read the actual invitation for the deadline, timezone, recipient/upload link and any format instruction. The repository brief allows a **Git bundle or private repository link**. The working repository is public with your approval. The easiest compliant route is the Git bundle in Step 5; it preserves commit history and does not require changing repository visibility. Do not send the public link as the only deliverable if the recruiter requires a private link or bundle.

## 2. Get a fresh copy on your laptop (5 minutes)
On Windows, open PowerShell and run these commands one at a time:

```powershell
git --version
py -3 --version
```
You need Git and Python 3.10 or newer. If a command is unavailable, install the missing prerequisite or share the exact error before proceeding. No Python packages, API keys or paid services are needed.

From a folder where you keep projects:

```powershell
git -c core.autocrlf=false clone https://github.com/sadad54/mindhive-backendAIEng-assessment.git mindhive-submission-check
cd mindhive-submission-check
git rev-parse HEAD
```
Use a fresh folder name if that folder already exists. Keep the printed commit SHA: it identifies exactly what you tested. Repository attributes preserve source/data bytes across platforms so hash checks are meaningful. On macOS/Linux use `python3` in place of `py -3` below.

## 3. Run the mandatory checks (usually a few minutes)
Run one command at a time. If one fails, stop and share the full error; do not edit labels, policy, expected values or thresholds just to make it pass.

```powershell
py -3 audit_data.py
py -3 -m unittest discover -s tests -v
py -3 regression_check.py
```
Expected: all **13 original imported files** verify; **56 tests** pass; regression check prints PASS. The original vendor/starter files are intentionally preserved, so use the fixed sync tests rather than treating the original symptom reporter as the solution.

Now measure the frozen matcher on your laptop, writing the new evidence outside the repository:

```powershell
py -3 evaluate_matcher.py --repeat 2 --output ../laptop_evaluation.json
py -3 regression_check.py --report ../laptop_evaluation.json
```
Expected mature validation counts: **114 lines, 26 automatic decisions, all 26 correct, zero wrong**. Timing will differ from the saved host report. The second command must pass, including warm p95 <=250 ms. Development/all-train numbers are not independent test results. Calibration is not refitted by either command.

Verify deterministic holdout output:

```powershell
py -3 predict.py
py -3 regression_check.py
```
Expected: **300 rows**, 94 auto, 205 review, 1 reject. This is an output count, not holdout accuracy. Do not manually change predictions. **Do not run fit_policy.py as part of submission**: the policy is already frozen and validation has been inspected.

Measure and verify the report:

```powershell
py -3 starter/make_perf_db.py --out data/perf.sqlite
py -3 perf_verify.py --output ../laptop_perf.json
```
Expected: **8,666 rows**, `strict_reference_equality: True`, `p95_oracle_all_rows: True`, `within_budget: True`. Five-run median must be <=10 seconds on your laptop. The database is generated locally and excluded from the Git bundle. This verifies the fast rewrite; **never run the original report_query.sql over the full database window**.

Finally:

```powershell
git status --short
```
Expected: no output. Laptop JSON results are outside the repository; generated databases/caches are ignored; deterministic predictions should not change. If files appear, inspect them and share the output instead of discarding or blindly committing changes. Keep laptop_evaluation.json and laptop_perf.json as genuine local evidence.

## 4. Prepare to defend your work (90–120 minutes)
Read in this order:
1. README.md: scope, commands, measured results and deliberate limits.
2. DESIGN.md: objective, pipeline, boundaries and cost assumptions.
3. matcher/service.py: trace one input through retrieval, guards, confidence group and decision.
4. EVAL.md: final results, confidence groups and your 20 personal case reviews.
5. DECISIONS.md: for each choice, explain the rejected alternative and reversal trigger.
6. PERF.md and perf_report.py: why order-day and event-day populations differ, why repeated scans are expensive, how exact p95 is computed.
7. SYNC.md and sync_fixed/adapter.py: stable retry key/base version, atomic cursor, outbox, conflict handling and vendor limits.
8. SCALE.md and WALKTHROUGH.md: production limits and live-change exercises.

Say these explanations out loud in your own words:
- Why can an exact product name still require review? Use the standard/Bulk cases.
- Why do 26/26 correct validation autos NOT prove 100% future accuracy or a guaranteed 98% population precision?
- Why does changing the wrong-match cost from 20x to 3x affect the operating point but not permit cross-tenant matches?
- Why can a barcode support omitted information but not erase contradictory text?
- Why does the confidence model treat exact and non-exact text differently on this dataset? What could go wrong on new data?
- What happens if the process dies immediately after the ERP commits a write?
- What does the vendor API make impossible to guarantee?

Use the assessment's 60-minute structure: 10 minutes problem framing, 20 minutes defence, 20 minutes live change, 10 minutes your questions. Practice a small change on a separate branch, not submitted main. Explain the invariant first, add a failing fixture, make the change, and rerun the relevant tests. Do not weaken a gate to disguise a failure. If you cannot explain a module, that is the next preparation task to work through together.

## 5. Create and verify the submission bundle (2 minutes)
After all checks pass and the working tree is clean, remain in the cloned repository:

```powershell
git rev-parse HEAD
git bundle create ../mindhive-assessment.bundle --all
git bundle verify ../mindhive-assessment.bundle
```
Expected: bundle verification succeeds. The file is one folder above your repository and contains the committed source, data, predictions, documents and commit history. It does not include the generated performance database or uncommitted laptop outputs.

If the recruiter explicitly asks for a private repository instead, follow that access workflow and ensure the named reviewers can read it. Do not alter visibility or reviewer permissions blindly. No submission message or access change has been made on your behalf.

## 6. Submit and keep the tested version (2 minutes)
Use the actual invitation's upload/email channel. Attach the bundle, state the tested commit SHA and identify README.md as the entry point. If permitted, include the two laptop JSON reports as separate measurement evidence. Keep the AI attribution and known limitations intact. Do not claim holdout precision or a laptop runtime you did not measure.

After submission, preserve the tested commit. Continue interview practice on a separate branch so you can reproduce exactly what the reviewers received.

## Final personal checklist
- [ ] Deadline/timezone and requested channel confirmed.
- [ ] Fresh laptop copy passes integrity, all tests and regression checks.
- [ ] Laptop matcher p95 <=250 ms and report median <=10 seconds, with saved evidence.
- [ ] Predictions remain deterministic and the Git working tree is clean.
- [ ] I can explain the personal reviews and defend the decision log without memorised answers.
- [ ] Git bundle verifies, or requested private access has been checked.
- [ ] Submitted SHA recorded; no unsupported accuracy, timing or authorship claims.
