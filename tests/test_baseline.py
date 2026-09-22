import tempfile
import unittest
from dataclasses import fields
from pathlib import Path

from evaluate import p95, run, summarise
from matcher.core import Candidate, Result, ReviewMatcher, validate_result
from matcher.data import Catalogue, OrderLine, load_labelled


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.line = OrderLine("L1", "acme", "C1", "2026-01-01", "disc")
        self.catalogue = Catalogue({
            "acme": {"A": {"disabled": "0", "item_name": "disc"},
                     "OLD": {"disabled": "1", "item_name": "old disc"}},
            "nordic": {"N": {"disabled": "0", "item_name": "milk"}}})

    def test_cross_tenant_accepted_code_and_candidate_are_rejected(self):
        for result in (Result("N", .99, "auto", "barcode_hit", (Candidate("N", .99),)),
                       Result(candidates=(Candidate("N", .99),))):
            with self.assertRaises(ValueError):
                validate_result(self.line, result, self.catalogue)

    def test_disabled_target_cannot_be_accepted(self):
        with self.assertRaises(ValueError):
            validate_result(self.line, Result("OLD", .99, "auto", "barcode_hit", (Candidate("OLD", .99),)), self.catalogue)

    def test_nan_and_review_with_code_are_rejected(self):
        for result in (Result(confidence=float("nan")), Result(item_code="A")):
            with self.assertRaises(ValueError):
                validate_result(self.line, result, self.catalogue)

    def test_all_review_precision_is_undefined(self):
        stats = summarise([(self.line, "A", Result()), (self.line, "", Result())])
        self.assertIsNone(stats["precision"])
        self.assertEqual(stats["coverage"], 0)
        self.assertEqual(stats["accuracy_including_correct_abstention"], .5)
        self.assertEqual(stats["utility_seconds_equivalent"], -80)
        self.assertEqual(stats["recall_at_3"], 0)

    def test_mixed_decisions_metrics_and_candidate_recall(self):
        accepted = Result("A", .99, "auto", "test", (Candidate("A", .99),))
        review = Result(candidates=(Candidate("A", .8),))
        stats = summarise([(self.line, "A", accepted), (self.line, "", accepted),
                           (self.line, "A", review), (self.line, "", Result(decision="reject", reason_code="not_an_item"))])
        self.assertEqual(stats["precision"], .5)
        self.assertEqual(stats["coverage"], .5)
        self.assertEqual(stats["utility_seconds_equivalent"], -860)
        self.assertEqual(stats["improvement_over_all_review"], -700)
        self.assertEqual(stats["recall_at_3"], 1)
        self.assertEqual(stats["recall_at_3_on_answerable_abstentions"], 1)
        self.assertEqual(stats["blank_label_abstention_rate"], .5)

    def test_label_boundary_and_leading_zero_identifier(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "train.csv"
            path.write_text("line_id,tenant,customer_id,order_date,raw_text,buyer_sku,gt_item_code\nL1,acme,C1,2026-01-01,disc,00123,A\n")
            lines, labels = load_labelled(path)
            self.assertEqual(lines[0].buyer_sku, "00123")
            self.assertEqual(labels, {"L1": "A"})
            self.assertNotIn("gt_item_code", {field.name for field in fields(lines[0])})
            path.write_text(path.read_text() + "L1,acme,C1,2026-01-01,disc,00123,A\n")
            with self.assertRaises(ValueError):
                load_labelled(path)

    def test_unknown_tenant_reviews_without_fallback(self):
        line = OrderLine("U", "unknown", "C", "2026-01-01", "disc")
        result = ReviewMatcher(self.catalogue).match(line)
        self.assertEqual(result.reason_code, "unknown_tenant")
        validate_result(line, result, self.catalogue)

    def test_nearest_rank_p95(self):
        self.assertEqual(p95(list(range(1, 21))), 19)
        self.assertEqual(p95([7]), 7)
        self.assertIsNone(p95([]))

    def test_supplied_data_baseline(self):
        data = Path(__file__).resolve().parents[1] / "data"
        result = run(data, repeat=1)
        self.assertEqual(result["overall"]["lines"], 420)
        self.assertEqual(result["overall"]["unanswerable"], 125)
        self.assertEqual(result["overall"]["review"], 420)
        self.assertEqual(result["overall"]["utility_seconds_equivalent"], -16800)


if __name__ == "__main__":
    unittest.main()
