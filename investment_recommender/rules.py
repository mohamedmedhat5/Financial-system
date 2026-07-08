"""
rules.py
========
The actual "rules" of the rule-based recommendation engine, expressed as
plain data tables rather than scattered if/elif logic. Centralizing them
here means tuning the system (e.g. "give Medium-risk investors a bit more
Gold") is a one-line data edit, not a code change -- and it makes it easy
to later swap this whole module for a learned/statistical model without
touching recommendation_engine.py's public interface.
"""

from decimal import Decimal


# ---------------------------------------------------------------------------
# Duration buckets
# ---------------------------------------------------------------------------
SHORT_MAX_YEARS = Decimal("3")   # 0-3 years  -> "SHORT"
MEDIUM_MAX_YEARS = Decimal("7")  # 3-7 years  -> "MEDIUM", anything above -> "LONG"


# ---------------------------------------------------------------------------
# Base allocation matrix: (risk_tolerance, duration_bucket) -> % per asset.
# Every row sums to exactly 100.
#
# The three rows marked "(given)" reproduce the sample rules from the brief
# verbatim. The other six are interpolated so that, reading across any row
# or down any column, the "safe" share (Bonds + Gold) decreases
# monotonically as risk tolerance and/or duration increase -- the property
# a sane allocation rule set should have.
# ---------------------------------------------------------------------------
BASE_ALLOCATION_MATRIX = {
    ("LOW", "SHORT"):     {"BONDS": 70, "GOLD": 30, "ETFS": 0,  "STOCKS": 0},   # given
    ("LOW", "MEDIUM"):    {"BONDS": 60, "GOLD": 25, "ETFS": 15, "STOCKS": 0},
    ("LOW", "LONG"):      {"BONDS": 50, "GOLD": 20, "ETFS": 25, "STOCKS": 5},

    ("MEDIUM", "SHORT"):  {"BONDS": 40, "GOLD": 25, "ETFS": 25, "STOCKS": 10},
    ("MEDIUM", "MEDIUM"): {"BONDS": 20, "GOLD": 30, "ETFS": 30, "STOCKS": 20},  # given
    ("MEDIUM", "LONG"):   {"BONDS": 15, "GOLD": 20, "ETFS": 35, "STOCKS": 30},

    ("HIGH", "SHORT"):    {"BONDS": 20, "GOLD": 20, "ETFS": 30, "STOCKS": 30},
    ("HIGH", "MEDIUM"):   {"BONDS": 10, "GOLD": 15, "ETFS": 30, "STOCKS": 45},
    ("HIGH", "LONG"):     {"BONDS": 5,  "GOLD": 10, "ETFS": 25, "STOCKS": 60},  # given
}


# ---------------------------------------------------------------------------
# Goal adjustments: percentage-point shifts applied on top of the base
# allocation. Every adjustment row sums to zero, so applying it never
# changes the *total* -- it only redistributes between assets. If a shift
# would push an asset below 0%, it's clipped to 0, and the whole allocation
# is renormalized back to exactly 100% in recommendation_engine.py.
# ---------------------------------------------------------------------------
GOAL_ADJUSTMENTS = {
    # Prioritize stability: more Bonds/Gold, less ETFs/Stocks.
    "CAPITAL_PRESERVATION": {"BONDS": 10, "GOLD": 5, "ETFS": -5, "STOCKS": -10},
    # Prioritize long-run growth: less Bonds/Gold, more ETFs/Stocks.
    "WEALTH_GROWTH": {"BONDS": -10, "GOLD": -5, "ETFS": 5, "STOCKS": 10},
    # Prioritize regular income: more Bonds (coupons) and ETFs (often
    # dividend-paying), less non-yielding Gold and volatile growth Stocks.
    "PASSIVE_INCOME": {"BONDS": 10, "GOLD": -5, "ETFS": 5, "STOCKS": -10},
}


# ---------------------------------------------------------------------------
# Text fragments used by explanations.py to build human-readable reasoning.
# ---------------------------------------------------------------------------
ASSET_DESCRIPTIONS = {
    "BONDS": "Bonds pay regular, predictable interest and are the most stable asset here, anchoring the portfolio against market swings.",
    "GOLD": "Gold is a non-correlated hedge against inflation and market shocks, protecting purchasing power when other assets fall.",
    "ETFS": "ETFs spread money across many companies or sectors at once, giving diversified market growth without single-stock risk.",
    "STOCKS": "Stocks offer the highest long-term growth potential of the four asset classes, in exchange for the most short-term volatility.",
}

RISK_REASONS = {
    "LOW": "Because you chose a LOW risk tolerance, the engine weighted the portfolio toward Bonds and Gold to minimize the chance of losing money.",
    "MEDIUM": "Because you chose a MEDIUM risk tolerance, the engine balanced stable assets (Bonds, Gold) against growth assets (ETFs, Stocks) roughly evenly.",
    "HIGH": "Because you chose a HIGH risk tolerance, the engine weighted the portfolio toward ETFs and Stocks to maximize long-term growth.",
}

DURATION_REASONS = {
    "SHORT": "With a SHORT time horizon ({years} years), the engine reduced exposure to Stocks/ETFs, since there's less time to recover from a downturn before the money is needed.",
    "MEDIUM": "With a MEDIUM time horizon ({years} years), the engine allowed a moderate amount of Stocks/ETFs, since there's some time to ride out volatility.",
    "LONG": "With a LONG time horizon ({years} years), the engine increased exposure to Stocks/ETFs, since there's enough time for growth assets to recover from downturns.",
}

GOAL_REASONS = {
    "CAPITAL_PRESERVATION": "Your goal of Capital Preservation further shifted weight toward Bonds and Gold, since protecting the principal matters more than maximizing growth.",
    "WEALTH_GROWTH": "Your goal of Wealth Growth further shifted weight toward ETFs and Stocks, since maximizing long-term returns matters more than short-term stability.",
    "PASSIVE_INCOME": "Your goal of Passive Income further shifted weight toward income-generating Bonds and ETFs, and away from non-yielding Gold and growth-focused Stocks.",
}

ASSET_DISPLAY_NAMES = {"BONDS": "Bonds", "GOLD": "Gold", "ETFS": "ETFs", "STOCKS": "Stocks"}
