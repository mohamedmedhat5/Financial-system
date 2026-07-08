"""
recommendation_engine.py
=========================
The rule-based decision layer: given a validated InvestorProfile, decide
WHAT percentage of the portfolio goes into Bonds, Gold, ETFs, and Stocks.

This module deliberately knows nothing about money amounts (that's
portfolio_allocator.py's job) or about explanation text (that's
explanations.py's job) -- it only answers "what percentages?". That
separation is what makes it possible to later swap this module for a
machine-learned or NLP-driven engine without touching the rest of the
system: any replacement only needs to expose the same
`generate_allocation()` signature.
"""

from decimal import Decimal
from typing import Dict

from .models import InvestorProfile
from .rules import BASE_ALLOCATION_MATRIX, GOAL_ADJUSTMENTS
from .utils import distribute_exact

ASSET_CODES = ("BONDS", "GOLD", "ETFS", "STOCKS")


class RecommendationEngine:
    """Applies the rule tables in rules.py to a single InvestorProfile."""

    def __init__(self, profile: InvestorProfile):
        self.profile = profile

    def generate_allocation(self) -> Dict[str, Decimal]:
        """Return {asset_code: percentage}, with percentages summing to
        EXACTLY Decimal('100.00')."""
        duration_bucket = self.profile.duration_bucket()
        risk = self.profile.risk_tolerance.value
        goal = self.profile.goal.value

        base = BASE_ALLOCATION_MATRIX[(risk, duration_bucket)]
        adjustment = GOAL_ADJUSTMENTS.get(goal, {})

        # Apply the goal's percentage-point shift on top of the base rule,
        # clipping anything that would go negative (e.g. Stocks is already
        # 0% for LOW/SHORT and can't go to -10%).
        adjusted = {
            asset: max(Decimal(base.get(asset, 0)) + Decimal(adjustment.get(asset, 0)), Decimal("0"))
            for asset in ASSET_CODES
        }

        # Clipping above can make the row sum to something other than 100
        # (e.g. 110, if two assets got clipped at 0 instead of going more
        # negative). distribute_exact() renormalizes the weighted values
        # back to a clean, exact 100% split, preserving their relative
        # proportions.
        return distribute_exact(Decimal("100"), adjusted, places="0.01")

    def describe_rule_inputs(self) -> Dict[str, str]:
        """Expose which rule-table row/adjustment fired -- useful for
        transparency, logging, or for explanations.py to build on."""
        return {
            "risk_tolerance": self.profile.risk_tolerance.value,
            "duration_bucket": self.profile.duration_bucket(),
            "goal": self.profile.goal.value,
        }
