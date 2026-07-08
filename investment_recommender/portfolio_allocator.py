"""
portfolio_allocator.py
=======================
Converts the engine's percentage allocation into actual monetary amounts,
guaranteeing the per-asset amounts add up to EXACTLY the investor's total
(no cent lost or gained to rounding -- see utils.distribute_exact).
"""

from decimal import Decimal
from typing import Dict, List

from .models import AllocationItem, AssetClass
from .utils import distribute_exact

ASSET_ORDER = ("BONDS", "GOLD", "ETFS", "STOCKS")


class PortfolioAllocator:
    """Pure conversion layer: percentages + a total amount -> money amounts.
    Knows nothing about *why* the percentages are what they are -- that
    keeps it reusable even if the engine's rules change completely."""

    @staticmethod
    def allocate(amount: Decimal, percentages: Dict[str, Decimal]) -> List[AllocationItem]:
        total_pct = sum(percentages.values())
        if abs(total_pct - Decimal("100")) > Decimal("0.05"):
            raise ValueError(
                f"Allocation percentages must sum to 100%, got {total_pct}%. "
                "This indicates a bug in the recommendation engine's rounding."
            )

        amounts = distribute_exact(amount, percentages, places="0.01")

        items = [
            AllocationItem(
                asset=AssetClass(asset_code),
                percentage=percentages[asset_code],
                amount=amounts[asset_code],
            )
            for asset_code in ASSET_ORDER
        ]

        # Largest allocation first -- purely for display purposes.
        items.sort(key=lambda item: item.percentage, reverse=True)
        return items
