"""
models.py
=========
Plain data classes describing the system's core entities. Using
dataclasses and Enums (rather than loose dicts/strings) gives every other
module a typed, self-documenting contract to depend on, and lets typos
like "Meduim" fail loudly instead of silently producing a wrong portfolio.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from .utils import classify_duration


class RiskTolerance(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class InvestmentGoal(str, Enum):
    CAPITAL_PRESERVATION = "CAPITAL_PRESERVATION"
    WEALTH_GROWTH = "WEALTH_GROWTH"
    PASSIVE_INCOME = "PASSIVE_INCOME"


class AssetClass(str, Enum):
    BONDS = "BONDS"
    GOLD = "GOLD"
    ETFS = "ETFS"
    STOCKS = "STOCKS"


@dataclass
class InvestorProfile:
    """The validated, structured input collected from a user -- whether
    they typed it into the interactive CLI prompts, or it was extracted
    from free text by nlp_parser.py."""

    amount: Decimal
    duration_years: Decimal
    risk_tolerance: RiskTolerance
    goal: InvestmentGoal
    raw_text: Optional[str] = None  # original sentence, if collected via NLP

    def duration_bucket(self) -> str:
        """SHORT / MEDIUM / LONG, per the thresholds in rules.py."""
        return classify_duration(self.duration_years)


@dataclass
class AllocationItem:
    """One line of a recommended portfolio: a single asset class with its
    share of the money and the reasoning behind that share."""

    asset: AssetClass
    percentage: Decimal
    amount: Decimal = Decimal("0.00")
    explanation: str = ""


@dataclass
class PortfolioRecommendation:
    """The full output of the engine: a profile plus its allocation lines."""

    profile: InvestorProfile
    items: List[AllocationItem] = field(default_factory=list)
    summary: str = ""

    def total_percentage(self) -> Decimal:
        return sum((item.percentage for item in self.items), Decimal("0"))

    def total_amount(self) -> Decimal:
        return sum((item.amount for item in self.items), Decimal("0"))
