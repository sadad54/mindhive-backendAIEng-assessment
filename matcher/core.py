"""Result contract and honest no-automation baseline; no confidence model yet."""
import math
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    item_code: str
    score: float


@dataclass(frozen=True)
class Result:
    item_code: str = ""
    confidence: float = 0.0
    decision: str = "review"
    reason_code: str = "baseline_review"
    candidates: tuple[Candidate, ...] = ()


def validate_result(line, result, catalogue):
    if result.decision not in {"auto", "review", "reject"}:
        raise ValueError("Unknown decision")
    if not math.isfinite(result.confidence) or not 0 <= result.confidence <= 1:
        raise ValueError("Confidence must be finite and in [0,1]")
    if not re.fullmatch(r"[a-z][a-z0-9_]*", result.reason_code):
        raise ValueError("Invalid reason token")
    if (result.decision == "auto") != bool(result.item_code):
        raise ValueError("Only auto decisions must contain item_code")
    if result.item_code and not catalogue.eligible(line.tenant, result.item_code):
        raise ValueError("Wrong tenant or ineligible accepted item")
    if len(result.candidates) > 3:
        raise ValueError("At most three candidates")
    codes = [candidate.item_code for candidate in result.candidates]
    if len(set(codes)) != len(codes):
        raise ValueError("Duplicate candidates")
    for candidate in result.candidates:
        if not catalogue.eligible(line.tenant, candidate.item_code):
            raise ValueError("Wrong tenant or ineligible candidate")
        if not math.isfinite(candidate.score) or not 0 <= candidate.score <= 1:
            raise ValueError("Candidate score must be finite and in [0,1]")
    if tuple(sorted(result.candidates, key=lambda c: (-c.score, c.item_code))) != result.candidates:
        raise ValueError("Candidates must be sorted by score descending, code ascending")
    if result.item_code and (not codes or codes[0] != result.item_code):
        raise ValueError("Accepted code must be the first candidate")


class ReviewMatcher:
    def __init__(self, catalogue):
        self.catalogue = catalogue

    def match(self, line):
        reason = "baseline_review" if line.tenant in self.catalogue.by_tenant else "unknown_tenant"
        return Result(reason_code=reason)
