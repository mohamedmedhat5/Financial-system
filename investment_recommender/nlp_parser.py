"""
nlp_parser.py
=============
PLACEHOLDER for future natural-language input support.

Goal: let a user eventually type something like

    "I have 100,000 EGP and want to invest for 5 years with medium risk."

and have the system extract amount / duration / risk tolerance / goal
automatically, pre-filling (or skipping) the interactive prompts in
main.py.

Today this is implemented with simple regular expressions and keyword
matching -- good enough to demo the end-to-end flow, but not "real" NLP.
The function signature, `parse(text) -> dict`, is deliberately the ONLY
thing the rest of the system depends on: main.py never inspects *how*
the dict was produced. That means this whole module can later be swapped
for a call to spaCy, a fine-tuned classifier, or an LLM, with zero
changes anywhere else in the codebase.

Returned dict keys (any may be missing if not confidently found in the text):
    "amount"          -> Decimal
    "duration_years"  -> Decimal
    "risk_tolerance"  -> "LOW" | "MEDIUM" | "HIGH"
    "goal"            -> "CAPITAL_PRESERVATION" | "WEALTH_GROWTH" | "PASSIVE_INCOME"
"""

import re
from decimal import Decimal
from typing import Dict, Optional

_AMOUNT_PATTERN = re.compile(r"([\d,]+(?:\.\d+)?)\s*(k|thousand|m|million)?", re.IGNORECASE)
_DURATION_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*(years?|yrs?)", re.IGNORECASE)

_RISK_KEYWORDS = {
    "LOW": ["low risk", "low-risk", "conservative", "safe", "cautious", "risk-averse"],
    "MEDIUM": ["medium risk", "medium-risk", "moderate", "balanced"],
    "HIGH": ["high risk", "high-risk", "aggressive", "risky", "bold"],
}

_GOAL_KEYWORDS = {
    "CAPITAL_PRESERVATION": ["preserve", "preservation", "protect my money", "capital preservation", "safety of capital"],
    "WEALTH_GROWTH": ["grow my wealth", "wealth growth", "build wealth", "maximize growth", "long-term growth"],
    "PASSIVE_INCOME": ["passive income", "regular income", "dividend", "income generation", "monthly income"],
}


def _extract_amount(text: str) -> Optional[Decimal]:
    """Picks the largest plausible number in the text (a crude heuristic,
    but works well for sentences like "I have 100,000 EGP ... for 5 years":
    it correctly prefers 100,000 over the much smaller "5")."""
    best = None
    for match in _AMOUNT_PATTERN.finditer(text):
        number_str, suffix = match.groups()
        if not number_str:
            continue
        digits_only = number_str.replace(",", "")
        if digits_only in ("", "."):
            continue
        try:
            value = Decimal(digits_only)
        except Exception:
            continue
        if suffix:
            suffix = suffix.lower()
            if suffix in ("k", "thousand"):
                value *= 1000
            elif suffix in ("m", "million"):
                value *= 1_000_000
        if value > 0 and (best is None or value > best):
            best = value
    return best


def _extract_duration(text: str) -> Optional[Decimal]:
    match = _DURATION_PATTERN.search(text)
    if not match:
        return None
    return Decimal(match.group(1))


def _extract_keyword(text: str, keyword_map: dict) -> Optional[str]:
    lowered = text.lower()
    for canonical, keywords in keyword_map.items():
        if any(keyword in lowered for keyword in keywords):
            return canonical
    return None


def parse(text: str) -> Dict[str, object]:
    """Best-effort extraction of structured fields from free text.

    Never raises -- fields that can't be confidently found are simply
    omitted from the returned dict, leaving them for the normal
    interactive/validated prompts in main.py to collect instead.
    """
    if not text or not text.strip():
        return {}

    result: Dict[str, object] = {}

    amount = _extract_amount(text)
    if amount is not None:
        result["amount"] = amount

    duration = _extract_duration(text)
    if duration is not None:
        result["duration_years"] = duration

    risk = _extract_keyword(text, _RISK_KEYWORDS)
    if risk is not None:
        result["risk_tolerance"] = risk

    goal = _extract_keyword(text, _GOAL_KEYWORDS)
    if goal is not None:
        result["goal"] = goal

    return result


if __name__ == "__main__":
    # Quick manual smoke test: python nlp_parser.py
    sample = "I have 100,000 EGP and want to invest for 5 years with medium risk."
    print(f"Input:  {sample}")
    print(f"Parsed: {parse(sample)}")
