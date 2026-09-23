# Task 3 — Evaluation
Status: measured review-only baseline and development retrieval experiment; 20 guided personal reviews and specific label concerns recorded. Confidence calibration, final acceptance policy, validation evaluation and numeric regression gates remain incomplete.

## Reproduction and provenance
```bash
python3 audit_data.py
python3 -m unittest discover -s tests -v
python3 evaluate.py --repeat 5 --output reports/baseline_review.json
```
The saved JSON records SHA-256 hashes for consumed data and evaluator/matcher source, plus Python/platform. Supplied inputs are pinned by docs/INPUT_MANIFEST.json. Python 3.12.14 on Linux x86_64 was used for this run. Nine tests passed. Code is standard-library Python 3.10+.

## Baseline results
All 420 labelled lines were evaluated without tuning. This is full-train baseline reporting, not held-out validation. Labels are loaded separately and never appear in OrderLine, the matcher input.

| Metric | All | Acme | Nordic |
|---|---:|---:|---:|
| Lines | 420 | 260 | 160 |
| Answerable labels | 295 | 174 | 121 |
| Blank labels | 125 | 86 | 39 |
| Auto answers / wrong autos | 0 / 0 | 0 / 0 | 0 / 0 |
| Reviews | 420 | 260 | 160 |
| Coverage | 0% | 0% | 0% |
| Auto precision | Undefined | Undefined | Undefined |
| Accuracy including correct abstentions | 29.76% | 33.08% | 24.38% |
| Blank-label abstention rate | 100% | 100% | 100% |
| Recall@3 on answerable lines | 0% | 0% | 0% |

Cost convention U=20C-800W-40A yields -16,800 seconds-equivalent, exactly the all-review reference; improvement is zero. Correct blank-label abstentions count as correct for the displayed accuracy, showing why neither accuracy nor zero wrong autos alone establishes business value.

Precision denominator is auto answers; coverage denominator is all lines. Blank-label abstention denominator is all blank-labelled lines. Recall@3 excludes blank labels; separate answerable-abstention recall uses only answerable reviewed/rejected lines. Empty denominators are null, never falsely reported as 100%.

## Timing and determinism
One unmeasured full pass warms the component, followed by five passes (2,100 timed calls). Timing excludes evaluator validation, file reads and setup. Nearest-rank p95 is sorted sample ceil(0.95*n)-1. Every repeated result is compared to its first result.

Recorded preparation: 28.307 ms. Warm p95: 0.001233 ms. This is trivial review-only overhead on the execution host, not a completed matcher or a laptop benchmark. Timing varies across runs.

## Segmentation
Input-only flags: structured buyer SKU/barcode (77 lines), pack word (76), dimension/weight token (224), selected Malay word skru/ayam/susu (3), slash/double-space (65), other (107). Rules are in noise_flags; flags overlap and are proxies rather than annotated true noise classes. Full counts/metrics are in the report. In particular, this is not yet a robust typo or missing-attribute classification; expand only with justified, manually checked definitions.

## Next evaluation gates
Before tuning an actual matcher, fix a grouped development/validation strategy to limit near-duplicate/alias leakage. Then measure identifiers-only and lexical increments, calibration by lane with uncertainty, a threshold curve, cold-start behaviour and regression thresholds. Baseline confidence is 0 because there is no candidate; it is not a fitted confidence model. Removing aliases currently changes nothing because no matching uses them: the required mature-versus-cold-start behaviour is not yet delivered.

## Personal error analysis — Sadad
Twenty development-policy failures have now been discussed individually with Sadad and recorded below, with evidence, judgement, root-cause assessment, cost class and proposed response. Consolidated groups and safeguard tradeoffs follow the cases. AI organisation/refinements are attributed; no external adjudication has occurred.

## Label concerns — Sadad
Four specific concerns distilled from Sadad's reviews are listed under Specific label concerns for adjudication below. Original labels remain unchanged for primary metrics; any adjudicated sensitivity analysis must be separate.

## Regression gates
TODO: numeric thresholds based on baseline; zero tenant escapes, deterministic/schema checks, precision/coverage/cost guards, <=250 ms p95, versioned fixtures and benchmark refresh policy.

## Identifier evidence checkpoint (development only)
Commands: `python3 split_data.py`; `python3 inspect_identifiers.py`. Saved output: reports/identifier_development.json, including data/split/source hashes. All 17 tests pass.

A frozen deterministic grouped allocation has 306 development lines and 114 validation lines. Connected components link same tenant + supplied nonblank target, normalised text, customer-scoped buyer SKU, or barcode. Group SHA-256 modulo 4 assigns validation. This uses labels only to allocate item-disjoint groups, never as matcher input. The catalogues remain available to both partitions. It is not stratified and does not guarantee grouping every fuzzy near-duplicate. Normalising punctuation may over-group; small validation/lane populations will limit calibration. No identifier performance results were measured on validation; prior all-review full-train reporting was a no-tuning baseline.

| Retrieval-only result | Aliases available | No alias history |
|---|---:|---:|
| Development lines | 306 | 306 |
| Lines with eligible candidates | 27 | 9 |
| Lines with supplied target retrieved | 27 | 9 |
| Unique candidate with no detected issue | 15 | 8 |

These are not auto precision/coverage or proof of calibration. The evidence component is not yet wired to an acceptance policy. Multiple source targets, weak alias metadata, invalid/expired mappings, unknown identifiers and numeric inconsistencies are flagged. Metadata/conflict counts can overlap. Remaining work includes brand/material checks, quantity parsing, lexical retrieval, and confidence/policy evaluation. No final predictions generated.

## Lexical development experiment — an unsafe acceptance baseline
Command: `python3 inspect_lexical.py`. Raw report: reports/lexical_development.json (input/split/source hashes and environment included). Twenty-five tests pass.

Token cosine (55%) and character-trigram cosine (45%) retrieve tenant-eligible products. These initial weights and the 0.25 retrieval floor are engineering starting choices, not learned probabilities. Known attribute contradictions filter candidates; identifier conflict flags persist. Provisional policy proposals require no detected issue, >=0.05 top-two score margin and the listed similarity threshold. They are evaluated only on development data; no policy has been enabled.

Top-three retrieval contains the supplied target for 210/220 answerable development lines (95.45%). There are 306 total development lines. Retrieval can help human review, but this does not demonstrate safe automatic decisions.

| Similarity threshold | Proposals | Correct | Wrong | Precision | Coverage | Improvement vs review |
|---|---:|---:|---:|---:|---:|---:|
| 0.60 | 196 | 166 | 30 | 84.69% | 64.05% | -12840 |
| 0.70 | 191 | 161 | 30 | 84.29% | 62.42% | -13140 |
| 0.80 | 165 | 136 | 29 | 82.42% | 53.92% | -13880 |
| 0.85 | 149 | 121 | 28 | 81.21% | 48.69% | -14020 |
| 0.90 | 128 | 101 | 27 | 78.91% | 41.83% | -14460 |
| 0.95 | 98 | 73 | 25 | 74.49% | 32.03% | -14620 |
| 1.00 | 78 | 54 | 24 | 69.23% | 25.49% | -15000 |

Recorded preparation: 171.116 ms; warm retrieval p95: 43.118 ms across 306 calls after a warm pass. This is an execution-host experiment, not a laptop certification or repeated performance study.

All tested points lose utility against all-review. Increasing the score threshold does not monotonically improve precision; the score-1.0 group still disagrees with supplied labels. No automatic policy or calibrated confidence is justified yet. These results may combine implementation limitations, missing context, and questionable labels; do not assert which without case inspection. Preserve original labels for primary metrics.

The report's failure_review_queue contains 20 wrong *proposed* answers at threshold 0.90, with source text, label and candidates. These are genuine failures of the recorded experimental policy, not production auto decisions. Root cause, cost class and proposed fix are blank for Sadad's personal work. Extracting traces does not complete the required manual analysis or three label concerns.

Known limits: incomplete pack/quantity distinction, brand spelling not canonicalised as authoritative evidence, partial attribute vocabularies, and a single global score rule. Validation remains unscored for this experiment. Next decisions should follow the personal case review and development evidence, not repeated validation tuning.

## Personal review 01 — ACM-T-0009
Status: Sadad supplied his judgement in the guided review; clarification remains unresolved. AI organised the source evidence and edited this entry. This is 1 of 20 cases discussed, not completion of the full analysis.

**Observed failure:** The threshold-0.90 experimental policy proposes ACM-BALL0659 for `Remax/Ball/Valve/2"/SS304`; supplied gt_item_code is blank. Similarity is 1.0. This is a false-positive proposal against the official label, not an enabled production auto-match.

**Evidence:** The tenant's catalogue contains one exact-name match, disabled=0, available_qty=0, stock_uom=Nos and carton conversion 12. Order quantity is 50, with no UOM, buyer SKU or barcode. No price is supplied. Other inspected Remax 2-inch valves differ in material.

**Sadad's judgement:** The product appears correctly identified, but stock prevents current fulfilment. Flag the disagreement for label/business-rule clarification rather than immediately changing the identity matcher. Keeping the distinction permits a specific customer response and an inventory notification.

**Root-cause assessment:** Suspected specification/label ambiguity, not a confirmed label defect. We have not established that zero stock explains the blank label or that the catalogue stock snapshot represents inventory on the order date. Missing UOM is another unresolved detail; full quantity conversion is not inferred.

**Cost class:** Wrong-auto proposal under supplied labels (800 seconds-equivalent in our convention); if identity is confirmed, the operational issue is fulfilment rather than demonstrated wrong-product shipment.

**Proposed response:** Ask whether item resolution must abstain for unavailable stock and how inventory timing/UOM are treated in annotation. Preserve official labels and primary metrics. Record any adjudication separately. A production inventory message should use current verified stock and a defined fulfilment policy; notifications are outside this assessment's matching scope.

**Regression proposal (assistant-suggested, not yet implemented):** Under an explicitly confirmed identity-only contract, changing stock availability alone should not change the resolved product. If availability is a separate acceptance rule, test its review reason independently. Do not encode a per-line exception or replace the label before adjudication.

**Grouping:** First candidate in the specification/label-clarification group. No assumption that other blank-labelled cases share this cause.

## Personal review 02 — ACM-T-0022
Status: Sadad supplied judgement during guided review; clarification remains unresolved. AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes ACM-NITR0925 for Kanto Nitrile Glove M Blue; supplied label is blank. Wrong-auto proposal under official labels, not a live automatic decision.

**Evidence:** Exact active catalogue-name match; order 100 box versus stock 900 Box. Structured unit_price is 94.66 versus list_price 99.48. The price is absent from raw_text but is present in the order record.

**Sadad's judgement:** Price difference alone should not reject product identity. Escalate the discrepancy to the pricing/business owner for clarification rather than assume it changes the intended item.

**Root-cause assessment:** Suspected label/business-rule ambiguity; neither a label error nor the source of the price difference has been established. A discount, timing or data error is possible but unproven.

**Cost class:** Wrong-auto proposal against the official label (800 seconds-equivalent under our convention). Actual wrong-product shipment is not established by price mismatch.

**Proposed response:** Preserve original labels and reported metrics; clarify price semantics and any acceptance rule. Keep pricing escalation separate from identity resolution. Do not create an arbitrary price cutoff or silently change the supplied answer.

**Regression proposal (assistant-suggested):** Under a confirmed identity-only contract, an otherwise identical item request with a different commercial price should retain its identity; any price-related review rule needs separate evidence and tests.

**Grouping:** Specification/label clarification, with pricing evidence distinct from Case 1's inventory question.

## Personal review 03 — ACM-T-0062
Status: Sadad supplied judgement in guided review; unit/label clarification remains open. AI organised evidence and edited the entry.

**Observed failure:** Experimental policy proposes ACM-BALL0944 for Vermont/Ball/Valve/2"/Brass; official label is blank. It is a wrong-auto proposal against official labels, not an enabled production decision.

**Evidence:** Unique exact-name match after separator cleanup; active product, stock 12 Nos; requested quantity 2 with uom_text=unit. Catalogue supports Nos (factor 1) and Carton (factor 12). No order price, buyer SKU or barcode supplies further evidence.

**Sadad's judgement:** Product identity is supported; clarify the unit/conversion convention before changing the matcher. He suggested the customer may have used a generic term instead of the exact unit name; this is a possible explanation, not established customer intent.

**Root-cause assessment:** Suspected label/business-rule ambiguity with unresolved unit semantics. Nos is not the only supported UOM: carton is also available. Do not infer unit=Nos solely from familiarity, stock sufficiency or the proposed explanation.

**Cost class:** False-positive proposal under official labels (800 seconds-equivalent in our convention); an actual wrong-product shipment has not been established.

**Proposed response:** Confirm whether unit maps to Nos for this item/customer and whether UOM uncertainty is intended to block item-code resolution. Retain original labels and metrics pending adjudication. A confirmed scoped synonym can support normalisation; do not impose a universal conversion or a per-line label exception.

**Regression proposal (assistant-suggested):** Once the convention is confirmed, verify scoped unit/Nos equivalence and ensure carton retains factor 12. Without confirmation, preserve unresolved quantity evidence rather than silently converting.

**Grouping:** Specification/label clarification, specifically generic-unit interpretation. The proposed customer explanation must not be presented as a proven root cause.

## Personal review 04 — ACM-T-0079
Status: Sadad identified the unresolved pack variant and requested customer clarification. AI organised the evidence and edited this entry; the proposed safeguard is not yet implemented.

**Observed failure:** Experimental policy selects ACM-BALL0364 for Vermont Ball Valve 1/2" SS304, quantity 1 ctn. Supplied label is blank (abstain).

**Evidence:** Active standard ACM-BALL0364 and Bulk ACM-BALL0364B share brand, diameter and material, but carton factors are 12 and 144 Nos respectively. Both display zero stock. No barcode, buyer SKU or price distinguishes the two. Scores 1.0 and approximately 0.935 produce a margin above the experimental 0.05 threshold.

**Sadad's judgement:** Review the pack variant and ask whether Standard or Bulk was intended; a wrong choice changes quantity twelvefold. Assistant refinement: phrase the question as 12 or 144 valves per carton to make the choice concrete.

**Root cause:** Missing pack-variant ambiguity safeguard. Exact-name similarity and a score margin treated the extra Bulk token as sufficient distinction, although the order supplies no pack-count evidence. Zero stock is a separate fulfilment issue and is not needed to justify review here.

**Cost class:** Wrong-auto proposal against the official label, with potential wrong-pack and twelvefold quantity consequences. The 12x quantity difference does not imply a measured 12x monetary loss.

**Proposed fix:** Detect eligible product siblings sharing identity attributes but differing in item-specific pack conversions. Require disambiguating pack/identifier evidence before accepting one; otherwise return review with both codes and an ambiguous_pack reason. Keep confidence thresholds from overriding this guard.

**Regression proposal (assistant-suggested):** A one-carton request with these two pack variants must review. An explicit, nonconflicting pack count or verified unique identifier may resolve the variant; tests must preserve tenant isolation and check the correct conversion. Do not generalise the factors to other products.

**Grouping:** Missing pack-variant capability, distinct from Cases 1–3's unresolved label/business conventions. Original label retained.

## Personal review 05 — ACM-T-0082
Status: Sadad supplied judgement in guided review; clarification pending. AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes ACM-PVCP0447 for Hitex PVC Pipe 32mm Class E; official label is blank.

**Evidence:** Exact active catalogue-name match. Order quantity 6, uom_text=unit; catalogue stock_uom=Length, only listed conversion Length=1, available_qty=0. No order price, buyer SKU or barcode supplies further evidence.

**Sadad's judgement:** Six units could mean six individual pieces/lengths of the identified product. Clarify that interpretation before changing the matcher.

**Root-cause assessment:** Suspected unit/business-rule or label ambiguity, not an established identity error. A single catalogue UOM does not prove the customer's intended unit or define physical length per piece. Zero-stock fulfilment remains separate; stock timing relative to the order is unverified.

**Cost class:** Wrong-auto proposal against official labels (800 seconds-equivalent under our convention). Neither actual wrong-product shipment nor the annotation's reason is established.

**Proposed response:** Ask whether six individual lengths are intended and whether unit is an approved synonym for Length for this product/customer. Ask whether unit uncertainty or stock availability is supposed to block item-code resolution. Keep original labels and metrics unchanged until adjudication; do not invent a conversion.

**Regression proposal (assistant-suggested):** Under a confirmed unit-to-Length convention, six units should preserve product identity and mean six stock lengths. Unknown conventions retain review evidence; no conversion to metres or other physical quantity without a specified length.

**Grouping:** Specification/label clarification with generic-unit semantics (Case 3) and a separate stock concern (Case 1).

## Personal review 06 — ACM-T-0114
Status: Sadad supplied judgement in guided review. Grade and quantity clarification remain open; AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes ACM-SELF0720, Stallion Self Drilling Screw #10 x 1" Stainless 410, for text specifying Stainless without 410; supplied label is blank.

**Evidence:** One matching stainless variant was found; the other inspected same-brand/same-size variant is Zinc Plated. Order quantity 100 has no UOM. Stock unit is Packet; one carton contains 10 packets, with no pieces-per-packet conversion supplied here. Stock is 3 packets. Order/list prices are 432.52/442.19.

**Sadad's judgement:** Require confirmation of the grade and ask whether 100 means screws, packets or cartons. He also suggested that the only listed grade was probably intended. That is retained as a hypothesis, not confirmation or an authorised default.

**Root-cause assessment:** The score-based proposal did not require resolution of omitted grade/quantity details. Unique catalogue availability narrows candidates but does not establish customer requirements. The intended grade, quantity unit and reason for the blank annotation are not independently confirmed.

**Cost class:** Wrong-auto proposal against supplied labels, with potential material-specification or quantity error. Neither stock comparison nor price similarity resolves the unknown order unit.

**Proposed response:** Ask whether Stainless 410 is intended and what unit applies to 100. Accept an omitted grade by default only under an established, scoped business/customer convention, not because there is one stocked/listed option. Preserve supplied labels and avoid inferring pieces from packet/carton conversion.

**Regression proposal (assistant-suggested):** An unspecified critical grade without an approved default remains unresolved. Explicit 410 or a verified scoped default can resolve that attribute; a contradictory grade cannot. Test screws/packets/cartons separately and never assume a pieces-per-packet factor.

**Grouping:** Missing-specification handling plus quantity/UOM clarification. This is distinct from an explicit identifier/text contradiction.

## Personal review 07 — ACM-T-0123
Status: Sadad supplied judgement in guided review. AI organised evidence and edited the entry; quantity and pricing clarification remain open.

**Observed failure:** Experimental policy proposes ACM-NITR0671 for Bosco Nitrile Glove L Black; supplied label is blank.
**Evidence:** Exact active product-name match; request 2 unit, catalogue unit Box, stock 12 boxes; order/list prices 336.95/303.93.
**Sadad's judgement:** Retain the proposed identity while clarifying unit and price. He initially assumed two gloves would not be purchased; that purchasing assumption is not verified evidence that boxes were intended.
**Root-cause assessment:** Product identity appears supported, but generic unit semantics and the price discrepancy are unresolved. No confirmed label defect or price-error source.
**Cost class:** Wrong-auto proposal under official labels (800 seconds-equivalent); actual wrong-product shipment not established.
**Proposed response:** Ask whether two boxes are intended and clarify price basis separately. Do not infer packaging from typical buying behaviour or treat a price difference alone as an identity contradiction.
**Regression proposal (assistant-suggested):** Generic unit does not automatically map to Box without a confirmed scoped convention; price-only changes do not force a different identity under an identity-only contract.
**Grouping:** Supported identity with quantity/pricing clarification. Preserve original labels.

## Personal review 08 — ACM-T-0130
Status: Sadad supplied judgement in guided review; quantity/fulfilment unresolved. AI organised evidence and edited the entry.

**Observed failure:** Experimental policy proposes ACM-SELF0072 for Remax Self Drilling Screw #8 x 1" Zinc Plated; official label is blank.
**Evidence:** Exact active name match; quantity 5 with missing UOM. Stock unit Packet, carton factor 10 packets, available_qty=0. Order/list prices 295.06/300.31.
**Sadad's judgement:** Group with product-identity-supported but quantity/fulfilment-unresolved cases; ask whether 5 means packets or cartons.
**Root-cause assessment:** Missing quantity unit and separate stock constraint; these do not prove a different product identity or explain the annotation conclusively.
**Cost class:** Wrong-auto proposal against official labels (800 seconds-equivalent), with potential quantity error. Stock timing is not verified.
**Proposed response:** Clarify packets versus cartons before conversion; five cartons would be 50 packets under the supplied conversion, whereas five packets stays five packets. If individual screws were intended, an additional pieces-per-packet conversion would be needed. Do not derive it from carton factor or price. Keep fulfilment and price checks separate from identity and preserve official labels.
**Regression proposal (assistant-suggested):** Missing UOM remains unresolved; explicit Packet and Carton produce 5 and 50 stock packets respectively, without changing identity where no pack sibling ambiguity exists. No implicit pieces conversion.
**Grouping:** Supported identity with quantity/fulfilment clarification, related to Cases 1, 5 and 7.

## Personal review 09 — ACM-T-0134
Status: Sadad confirmed grouping with Case 4 after discussing the distinction between order quantity and catalogue pack variant. AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes standard ACM-HEXB0675 for Tolsen Hex Bolt M8x50 HDG, qty=50, uom=ctn; supplied label is blank.
**Evidence:** Standard ACM-HEXB0675 has 6 Pcs/carton; active Bulk ACM-HEXB0675B has 144 Pcs/carton. Both display zero stock. No order price, barcode or buyer SKU disambiguates. Fifty cartons could represent 300 or 7,200 pieces.
**Sadad's judgement:** After clarification that Bulk denotes a separate product code rather than a quantity-based threshold, classify with Case 4's pack-variant ambiguity. Ask whether the customer intends cartons of 6 or 144 pieces.
**Root cause:** Missing pack-sibling ambiguity safeguard. Knowing the order UOM and carton count does not determine which product's conversion applies. A high similarity/margin for the standard name does not resolve this.
**Cost class:** Wrong-auto proposal under official labels (800 seconds-equivalent); potential 24-fold quantity difference, not a measured 24-fold financial loss.
**Proposed fix:** Reuse Case 4's product-family/pack-conversion ambiguity check; review unless explicit pack or reliable identifier evidence selects a variant. Never infer Bulk from a large order or invent a quantity threshold without a supplied business contract. Stock is a separate issue.
**Regression proposal (assistant-suggested):** Fifty cartons without variant evidence must review with both candidates. Explicit standard/bulk pack evidence selects the corresponding conversion; changing carton count alone must not silently switch item code.
**Grouping:** Same missing pack-variant capability as Case 4. Original label retained.

## Personal review 10 — ACM-T-0142
Status: Sadad supplied judgement in guided review; unit and pricing questions remain unresolved. AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes ACM-PVCP1037 for Kanto PVC Pipe 25mm Class C; supplied label is blank.
**Evidence:** Exact active catalogue-name match; requested 100 pcs, catalogue stock unit Length with only Length=1 listed. Available stock is 150 lengths; order/list prices are 166.02/156.72. No barcode or buyer SKU disambiguates further.
**Sadad's judgement:** Retain the proposed identity and clarify whether 100 pcs means 100 full stock lengths. He also wants identity clarification because of the price discrepancy.
**Root-cause assessment:** Unresolved pieces-to-stock-length convention and pricing/label question. Price motivates verification but does not alone establish a wrong item or explain the blank label; no asserted cause such as discount, tax or stale pricing is proven.
**Cost class:** Wrong-auto proposal under official labels (800 seconds-equivalent), with possible quantity interpretation error. Stock sufficiency cannot be concluded until units agree.
**Proposed response:** Confirm the intended item and whether each piece is a full stock length; separately confirm the quoted price basis. Do not change the item code or invent a conversion solely to reconcile prices. Preserve official labels pending adjudication.
**Regression proposal (assistant-suggested):** A confirmed scoped pcs=Length convention allows 100 stock lengths; a request for cut sections requires specified lengths/conversion. A price-only change should not silently substitute another product.
**Grouping:** Supported identity with unit/pricing clarification, related to Cases 3, 5 and 7, not the pack-sibling ambiguity of Cases 4 and 9.

## Personal review 11 — ACM-T-0150
Status: Sadad supplied judgement in guided review; label/pricing clarification remains open. AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes ACM-SELF0108 for Vermont Self Drilling Screw #10 x 1" Zinc Plated; supplied label is blank.
**Evidence:** Exact active catalogue-name match; request 5 packets, stock unit Packet, displayed stock 150 packets. Order/list prices 125.04/117.45. No barcode or buyer SKU provides additional evidence.
**Sadad's judgement:** Flag for label/pricing-rule clarification rather than change the matcher. He would look for discrepancies in description, units or stock before questioning the match.
**Refinement:** Description or packaging contradictions can challenge identity, but stock availability alone concerns fulfilment. A UOM difference must be interpreted using supported conversions rather than automatically treated as a different item.
**Root-cause assessment:** Suspected annotation/business-rule ambiguity; price discrepancy alone does not establish identity error. No pricing mechanism or reason for the blank label has been proven.
**Cost class:** Wrong-auto proposal under official labels (800 seconds-equivalent); wrong-product shipment is not independently established.
**Proposed response:** Ask why this otherwise matching item/unit expects abstention and whether price differences have a defined acceptance rule. Verify price basis separately. Keep official labels and primary metrics unchanged; do not substitute another item to match price.
**Regression proposal (assistant-suggested):** Under a confirmed identity-only contract, varying commercial price or stock alone should not change the resolved item. Explicit description or pack contradictions must still trigger the appropriate guard.
**Grouping:** Label/pricing-rule clarification, related to Case 2, with no observed quantity-unit mismatch in this case.

## Personal review 12 — ACM-T-0157
Status: Sadad supplied judgement in guided review; annotation/business-rule clarification remains open. AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes ACM-PVCP0117 for Tolsen - PVC - Pipe - 25mm - Class - C; supplied label is blank.
**Evidence:** Active matching product after separator cleanup; request 6 lengths, stock unit Length, displayed stock 3 lengths. No order price, barcode or buyer SKU.
**Sadad's judgement:** Retain identity and flag insufficient stock. Clarify the meaning/reason of the label with the business. Inform the customer that partial fulfilment may be possible, obtain approval before proceeding, and notify fulfilment about restocking.
**Root-cause assessment:** Suspected conflation of identity resolution with fulfilment or an unresolved annotation rule. Blank is already defined as expected abstention; the unanswered question is why abstention was assigned here, not what blank means. The catalogue snapshot does not establish historical stock at the order date.
**Cost class:** Wrong-auto proposal under supplied labels (800 seconds-equivalent); a wrong product is not independently established. The visible operational issue is inability to cover six stock lengths with a snapshot of three.
**Proposed response:** Confirm live stock and the business rule for shortages; separate identity from fulfilment status. Present partial supply/backorder options without changing quantity, promising a restock date or shipping without authorisation. Inventory alerts follow the business workflow, not an automatic replenishment action by the matcher. Preserve official labels/metrics pending adjudication.
**Regression proposal (assistant-suggested):** Under a confirmed identity-only contract, changing available quantity from six to three retains the item code while a separate fulfilment check flags shortage. Partial fulfilment must not silently rewrite the order quantity.
**Grouping:** Supported identity with insufficient-stock/label clarification, related to Case 1. No observed unit mismatch here.

## Personal review 13 — ACM-T-0161
Status: Sadad confirmed review until both quantity unit and product variant are established, after guided discussion. AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes standard ACM-ANGL0411 for Hitex Angle Grinder Disc 4.5" Flap, quantity 5 with blank UOM; supplied label is blank.
**Evidence:** Active standard ACM-ANGL0411 and Bulk ACM-ANGL0411B have stock unit Packet, carton factors 10 and 144 respectively, and displayed stock 150 packets each. No order price, barcode or buyer SKU distinguishes them.
**Sadad's judgement:** Keep in review until both unit and product variant are established. His initial suggestion that confirming cartons alone was enough was revised after comparing the two carton sizes.
**Root cause:** Combined missing quantity-unit and pack-sibling ambiguity safeguards. The highest-scoring standard name does not determine whether five means packets or cartons, nor which item code applies.
**Cost class:** Wrong-auto proposal against official labels (800 seconds-equivalent), with potential pack and quantity error. Five standard cartons means 50 packets; five Bulk cartons means 720 packets.
**Proposed response:** Ask whether five means packets or cartons and which variant/pack size is intended. If cartons, ask whether each contains 10 or 144 packets. Even for packets, require evidence distinguishing codes or a verified business rule making them interchangeable; do not silently choose by stock or score.
**Regression proposal (assistant-suggested):** Confirming only Carton must preserve review while both pack variants remain. Explicit, consistent unit and variant evidence can resolve the order. Quantity or inventory changes alone must not switch the code.
**Grouping:** Same pack-variant capability gap as Cases 4 and 9, plus missing quantity unit as in Case 8. Original labels retained.

## Personal review 14 — ACM-T-0174
Status: Sadad supplied judgement in guided review. AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes standard ACM-HEXB0675 for Tolsen Hex Bolt M8x50, quantity 1 ctn; supplied label is blank.
**Evidence:** The text omits finish/material. Active same-brand/same-size variants include HDG standard (6 Pcs/carton, stock 0), HDG Bulk (144 Pcs/carton, stock 0), Zinc Plated (100 Pcs/carton, stock 40), Stainless 304 (100 Pcs/carton, stock 900), and Stainless 316 (24 Pcs/carton, stock 900). No price, barcode or buyer SKU resolves the choice.
**Sadad's judgement:** Ask the customer to specify finish/material and resolve any remaining variant ambiguity. Availability of a stainless variant does not justify selecting it instead of HDG because the request is still too vague.
**Root cause:** Missing required-attribute ambiguity handling: absence of a contradiction was treated as sufficient support even though multiple finishes/materials fit the underspecified text. HDG additionally has a pack-sibling ambiguity. Similarity ranking does not establish the omitted specification.
**Cost class:** Wrong-auto proposal under official labels (800 seconds-equivalent), with potential wrong-material/finish and pack-quantity consequences.
**Proposed response:** Keep in review; ask which finish/material is required, including the stainless grade if relevant. If HDG is selected, clarify 6 versus 144 pieces per carton. Inventory may inform fulfilment options after identification, but must not silently substitute a different specification. Original labels retained.
**Regression proposal (assistant-suggested):** An M8x50 request without finish/material must review when these siblings are eligible. Changing inventory alone must not resolve the ambiguity. Explicit finish/material narrows the family; selecting HDG alone must still preserve the pack ambiguity.
**Grouping:** Missing specification capability, related to Case 6; residual HDG pack ambiguity relates to Cases 4 and 9.

## Personal review 15 — ACM-T-0177
Status: Sadad supplied judgement in guided review; quantity-unit clarification remains open. AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes ACM-SELF0464 for Vermont Self Drilling Screw #10 x 1-1/2" Stainless 410; supplied label is blank.
**Evidence:** Active exact-name match after removing the leading bullet; brand, size and grade are explicit. Request is 3 unit; catalogue stock unit Packet, carton conversion 50 packets, displayed stock 40 packets. No pieces-per-packet conversion, order price, buyer SKU or order barcode is supplied.
**Sadad's judgement:** Retain the proposed identity while clarifying what 3 unit means; ask whether the customer intended cartons or packets.
**Root-cause assessment:** Supported product identity with unresolved generic-unit semantics. The missing unit convention does not independently establish an identity error or explain why the supplied label is blank.
**Cost class:** Wrong-auto proposal under official labels (800 seconds-equivalent), with possible quantity/fulfilment error. Three packets and three cartons represent 3 and 150 stock packets respectively.
**Proposed response:** Confirm packets versus cartons before converting or assessing stock sufficiency. If individual screws were intended, obtain a pieces-per-packet conversion rather than deriving it from the carton factor. Clarify whether unresolved quantity is intended to block item-code resolution; preserve official labels and metrics pending adjudication.
**Regression proposal (assistant-suggested):** Without an approved scoped convention, unit remains unresolved. Explicit Packet and Carton convert three to 3 and 150 packets respectively; no silent mapping to individual screws. Keep supported identity distinct from quantity and fulfilment status.
**Grouping:** Supported identity with quantity-unit clarification, related to Cases 3 and 8. No omitted grade in this case, unlike Case 6.

## Personal review 16 — ACM-T-0182
Status: Sadad supplied judgement in guided review; unit and label clarification remain open. AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes ACM-PVCP0541 for Stallion PVC Pipe 15mm Class E; supplied label is blank.
**Evidence:** Exact active catalogue-name match; request quantity 2 with blank UOM. Stock unit Length, only listed conversion Length=1, displayed stock 900 lengths. Structured order/list prices are 204.45/184.98. No buyer SKU or order barcode supplies further evidence.
**Sadad's judgement:** Retain the proposed identity and clarify the quantity unit. The price difference does not justify changing the product match because the description matches exactly.
**Root-cause assessment:** Supported identity with missing quantity-unit semantics and a separate pricing/label question. A single listed UOM does not prove the intended unit; neither the price difference nor the missing unit establishes that a different product was intended. The reason for the blank annotation remains unconfirmed.
**Cost class:** Wrong-auto proposal under official labels (800 seconds-equivalent), with potential quantity interpretation error; actual wrong-product shipment is not established.
**Proposed response:** Confirm whether two full stock lengths are intended. Clarify price basis separately without substituting a different item to reconcile prices. Ask whether unresolved quantity or a defined pricing rule explains expected abstention. Preserve original labels and primary metrics pending adjudication.
**Regression proposal (assistant-suggested):** Missing UOM remains unresolved without a confirmed scoped convention; explicit Length means two stock lengths, with no inferred metres or cut-section conversion. Under a confirmed identity-only contract, price-only changes must not silently change the product code.
**Grouping:** Supported identity with unit/pricing clarification, related to Cases 5 and 10; no observed product-attribute contradiction.

## Personal review 17 — ACM-T-0196
Status: Sadad supplied judgement in guided review; label/business-rule clarification remains open. AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes ACM-BALL0305 for Bosco Ball Valve 1/2" SS304; supplied label is blank.
**Evidence:** Exact active catalogue-name match. Request is 50 pcs; catalogue stock unit Nos, carton conversion 10 Nos, displayed stock 900 Nos. No order price, buyer SKU or order barcode supplies further evidence.
**Sadad's judgement:** Flag for label/business-rule clarification rather than change the matcher: the proposed product matches the description exactly, is active, and pcs and Nos appear compatible.
**Root-cause assessment:** Suspected annotation/business-rule ambiguity, not a confirmed label defect. The apparent pcs-to-Nos synonym is consistent with individual-item counting but should be confirmed under the applicable unit convention. With that equivalence, the displayed stock covers the request; the snapshot does not establish historical stock.
**Cost class:** Wrong-auto proposal under official labels (800 seconds-equivalent); no independent evidence here establishes a wrong-product shipment.
**Proposed response:** Confirm the pcs/Nos convention and ask why this line expects abstention despite matching identity attributes and apparently compatible units. Do not invent an identity mismatch to fit the label or silently relabel it. Preserve official labels and primary metrics; record any adjudication separately.
**Regression proposal (assistant-suggested):** Under a confirmed pcs=Nos convention, 50 pcs means 50 individual items while 50 cartons means 500. Preserve the unit distinction and product identity; stock-only changes affect fulfilment separately under an identity-only contract.
**Grouping:** Label/business-rule clarification with apparently compatible unit terminology; related to Case 3, but more specific than generic unit wording.

## Personal review 18 — ACM-T-0202
Status: Sadad explicitly applied Case 13's rule in guided review. AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes standard ACM-ANGL0411 for Hitex Angle Grinder Disc 4.5" Flap, quantity 12 with blank UOM; supplied label is blank.
**Evidence:** Active standard ACM-ANGL0411 and Bulk ACM-ANGL0411B use Packet as stock unit, with carton factors 10 and 144 packets respectively. Both display stock 150 packets. No order price, buyer SKU or order barcode resolves the variant.
**Sadad's judgement:** Apply Case 13's rule: keep in review until both quantity unit and product variant are established.
**Root cause:** Same combined missing-unit and pack-sibling ambiguity as Case 13. Changing the requested quantity from five to twelve supplies no new evidence about unit or variant.
**Cost class:** Wrong-auto proposal under official labels (800 seconds-equivalent), with possible wrong-pack/quantity consequences. Twelve standard cartons represent 120 packets; twelve Bulk cartons represent 1,728 packets.
**Proposed response:** Ask whether twelve means packets or cartons and which product variant is intended. If cartons, confirm 10 versus 144 packets per carton. Do not infer Bulk from order size or choose the variant whose stock happens to cover the request. Preserve official labels.
**Regression proposal (assistant-suggested):** Reuse Case 13's guard across quantities five and twelve: quantity-only changes must not resolve missing unit or variant evidence. Confirming only Carton still leaves the pack ambiguous; require consistent distinguishing evidence or an approved scoped business convention.
**Grouping:** Same capability gap as Case 13 and the pack ambiguity in Cases 4 and 9; this is another affected line, not a separate root cause.

## Personal review 19 — ACM-T-0212
Status: Sadad supplied judgement in guided review; quantity-unit clarification remains open. AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes ACM-SELF0989 for Stallion Self Drilling Screw #8 x 3/4" Stainless 410; supplied label is blank.
**Evidence:** Exact active catalogue-name match. Request is 100 ea; stock unit Packet, carton conversion 100 packets, displayed stock 3 packets. Pieces per packet is not supplied. Structured order/list prices are 287.79/251.54; no buyer SKU or order barcode supplies further evidence.
**Sadad's judgement:** Retain the identity and clarify what is counted by 100 ea (his wording: "100 for each item"). Insufficient stock cannot be concluded before resolving the unit.
**Assistant refinement:** Ask explicitly whether the customer means 100 individual screws or 100 packets. The phrase each item alone could leave the same ambiguity unresolved. This wording refinement does not assert a customer answer.
**Root-cause assessment:** Supported identity with unresolved each-to-stock-unit semantics. Comparing 100 ea directly with 3 packets would mix units. The carton conversion describes packets, not individual screws, and cannot supply the missing pieces-per-packet factor. The reason for the blank annotation remains unconfirmed.
**Cost class:** Wrong-auto proposal under official labels (800 seconds-equivalent), with potential quantity/fulfilment error; actual wrong-product shipment is not independently established.
**Proposed response:** Confirm the counted unit. If individual screws, obtain the pieces-per-packet conversion and applicable split-pack fulfilment policy before checking sufficiency; if packets, 100 exceeds the displayed stock of 3. Verify live stock before a fulfilment commitment. Clarify pricing separately rather than changing identity solely for a price difference. Preserve original labels and primary metrics.
**Regression proposal (assistant-suggested):** Do not compare quantities until units are compatible. Explicit 100 packets yields a shortage against 3 packets; 100 individual screws remains unconvertible without a pieces-per-packet factor. Carton=100 packets must never be interpreted as Packet=100 screws.
**Grouping:** Supported identity with quantity-unit clarification, related to Cases 8 and 15; additionally highlights invalid cross-unit stock comparison.

## Personal review 20 — ACM-T-0218
Status: Sadad supplied judgement in guided review. AI organised evidence and edited this entry.

**Observed failure:** Experimental policy proposes ACM-PVCP0471 for Tolsen PVC Pipe 40mm Class C; supplied label is blank.
**Evidence:** Exact active catalogue-name match. Request is 10 ea; stock unit Length with only Length=1 listed, displayed stock 0 lengths. Structured order/list prices are 5.38/4.70; no buyer SKU or order barcode supplies further evidence.
**Sadad's judgement:** Retain identity because the description matches and the product is active. Clarify the unit, inform the customer about zero stock, and request business-rule clarification for the price difference rather than change the matcher.
**Assistant refinement:** ea already means each; ask whether each refers to one full stock length. Confirm live stock before a customer-facing availability statement because the supplied snapshot may not represent the order date or current inventory.
**Root-cause assessment:** Supported identity with unresolved each-to-Length semantics, a separate stock constraint, and a pricing/annotation question. None establishes that another product was intended; the reason for the blank label is not confirmed.
**Cost class:** Wrong-auto proposal under official labels (800 seconds-equivalent); quantity/fulfilment and pricing concerns are present, but wrong-product shipment is not independently established.
**Proposed response:** Confirm whether ten full stock lengths are intended; communicate verified unavailability without silently substituting a product or promising replenishment. Clarify price basis and whether availability, unit uncertainty or pricing rules require abstention in this task. Preserve official labels and primary metrics pending adjudication.
**Regression proposal (assistant-suggested):** Under a confirmed identity-only contract, price/stock-only changes retain the item code while separate operational checks report their concerns. ea must not acquire an unsupported physical-length conversion.
**Grouping:** Supported identity with unit, stock and pricing clarification, combining the concerns in Cases 1, 5 and 16.

## Consolidated personal-review findings
All 20 judgements above were supplied by Sadad during one-at-a-time guided review. AI assembled evidence, refined wording and proposed regression tests; these suggestions are attributed separately. The cases are failures of the recorded development-only experimental acceptance policy, not enabled production decisions.

| Group | Cases | Finding and next action |
|---|---|---|
| Pack-variant ambiguity | 4, 9, 13, 18; residual ambiguity in 14 | Same missing capability: a score margin can favour the shorter standard name without evidence selecting its pack. Add a family/pack ambiguity guard. |
| Omitted specification | 6, 14 | Grade/finish requirements remain unresolved. Check eligible siblings and explicitly scoped defaults; catalogue uniqueness is not proof of customer intent. |
| Quantity-unit uncertainty | 3, 5, 6, 7, 8, 10, 13, 15, 16, 18, 19, 20 | Keep unit interpretation and conversions explicit. Whether this blocks item identity requires a clear task/business contract. Never invent conversion factors. |
| Label/business-rule clarification | 1, 2, 3, 5, 7, 8, 10, 11, 12, 15, 16, 17, 19, 20 | Supported identity can coexist with unresolved units, prices or fulfilment. These are suspected specification/annotation issues, not proven label defects or reasons to rewrite labels. |

Groups overlap. Twenty affected lines do not mean twenty independent bugs. No implementation exception for a reviewed line is justified. Pack/specification guards may lower coverage or over-abstain if families are grouped too broadly; explicit distinguishing evidence must still allow resolution. Overly broad unit synonyms can create quantity errors, while overly strict synonyms can cause unnecessary reviews. Keeping identity separate from fulfilment is useful only if consistent with the agreed output contract.

**Selection limitation:** These twenty traces are all Acme blank-label false-positive proposals from one development experiment. They do not constitute representative coverage of both tenants, answerable false negatives, or all noise types. Additional evaluation must cover those dimensions without presenting it as personal analysis already performed by Sadad.

## Specific label concerns for adjudication
The following consolidate Sadad's recorded judgements; they are claims of under-specification requiring clarification, not declarations that the labels are wrong.

| Line | Supplied label and concern | Proposed adjudication and production response |
|---|---|---|
| ACM-T-0022 (Case 2) | Blank despite exact active Kanto glove identity, matching Box unit and sufficient displayed stock; order price differs from list price. Why does price warrant identity abstention, if it does? | Ask the annotation/business owner whether price is an acceptance rule and verify its basis. Preserve identity evidence; route pricing discrepancy separately rather than select another item. |
| ACM-T-0150 (Case 11) | Blank despite exact active Vermont screw identity and request 5 packets against 150 packets; price differs. No observed description or unit contradiction explains abstention. | Obtain the annotation rationale and pricing policy. Retain official scoring; use a separate pricing review if required, without inventing a wrong-item diagnosis. |
| ACM-T-0157 (Case 12) | Blank for an exact active Tolsen pipe identity with explicit lengths; requested 6 versus displayed stock 3. It is unclear whether matching labels encode fulfilment eligibility. | Confirm whether shortage should block identity resolution and verify inventory timing. Report shortage separately under an identity-only contract; partial supply requires customer approval. |
| ACM-T-0196 (Case 17) | Blank despite exact active Bosco valve identity, apparently compatible pcs/Nos and sufficient displayed stock. The unit convention and abstention rationale are unspecified. | Confirm pcs=Nos and request the label rationale. Do not silently relabel; preserve identity evidence for review and resolve the business rule before enabling acceptance. |

Keep supplied labels for primary metrics. Any later adjudication must record rationale, reviewer, date and version separately; report sensitivity results separately, never inflate primary metrics with assumed corrections. No external adjudication has occurred.

## Implementation priorities after personal review
1. Add and test pack-sibling and omitted-attribute ambiguity guards on development data, including cases where explicit evidence resolves ambiguity.
2. Represent unresolved units without fabricating conversions or conflating fulfilment with identity. Document unresolved contract assumptions.
3. Re-run development evaluation, compare utility/precision/coverage and inspect remaining failures. Only then choose and freeze an acceptance/calibration policy for validation.
4. Complete the remaining numeric regression gates and final evaluation deliverables; these twenty reviews do not complete Task 3 or the overall assessment.

