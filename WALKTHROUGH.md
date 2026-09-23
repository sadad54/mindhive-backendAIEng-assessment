# Walkthrough preparation — personal work remaining

The assessment requires you to explain and modify your submission. Code completion does not replace this step. This guide is AI-authored; your answers should be your own.

## 10 minutes — the problem
Explain why the matcher resolves identity or abstains, and why wrong shipments outweigh review effort. Use your chosen utility formula and distinguish a theoretical probability threshold from evidence guards. Present validation 26/26 correct autos at 22.81% coverage, immediately explaining the small sample and the wide interval. Do not call observed 100% a guarantee. Explain why 94 holdout autos have no known accuracy.

## 20 minutes — defend choices and failures
Rehearse D-09 (reject unsafe similarity policy), D-10 (pack siblings), D-11 (confidence groups), D-12 (sync conflict safety), and the performance decision. For each: alternative, evidence, downside, reversal condition. Revisit Cases 4/13/18 together: quantity does not select a pack. Contrast Case 14's missing material with Cases 2/11's price-only label concerns. Explain why those concerns are unresolved rather than confirmed label errors.

Trace one order through identifiers -> lexical candidates -> guards -> bucket -> frozen confidence -> output. Show that labels never enter OrderLine. Explain why an identifier is not an early return. Describe the cold-start ablation, candidate recall and precision denominators.

For costs changing from 20x to 3x review: derive p>760/820 versus p>80/140 under the selected utility. Explain why tenant boundaries and known contradictions remain hard rules even if review becomes relatively expensive.

## 20 minutes — live change practice
Practice these on a separate local branch, keeping the submitted frozen policy/results intact:
1. Add a previously unseen trade synonym. Write a fixture where it helps plus one where it must not alter a size/grade. Explain why normalising before extraction can be risky.
2. Add a new pack naming pattern. Show a positive family, a different-material non-family and a conflicting identifier. Explain false-ambiguity coverage costs.
3. Change the accepted cost ratio through policy configuration; recompute expected utility without silently refitting calibration on validation.
4. Reduce latency budget. Profile candidate generation; keep the exhaustive matcher as a recall oracle while trying bounded retrieval.
5. Simulate an ERP timeout after commit followed by process death and cache expiry. Show the same outbox key/base on restart and no forced rebase.

A strong explanation names the invariant before editing, shows the failing case, makes a small change, and reruns the relevant test plus regression gates. If a gate fails, explain it rather than weakening it to pass.

## 10 minutes — questions for the team
Ask whether identity labels intentionally encode stock/pricing/UOM eligibility; who owns alias adjudication and review capacity; what delayed wrong-shipment feedback is available; and whether the ERP offers snapshot pagination or durable operation lookup.

## Before submission
- Run the README commands on your own laptop and record genuine timing differences.
- Read every enabled policy group and inspect one positive/negative example yourself.
- Explain the report's order-day versus event-day populations and nearest-rank p95.
- Explain why the sync cannot guarantee deletion detection with this vendor API.
- Confirm private-link/bundle submission format; do not assume the public working repository is the required submission channel.
- Ensure you can defend all logged choices without memorising this document.
