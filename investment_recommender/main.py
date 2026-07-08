"""
main.py
=======
Command-line entry point for the Investment Recommendation System.

Usage:
    python main.py                  Interactive mode: prompts for every input.
    python main.py --demo           Runs 3 built-in sample profiles, no input needed.
    python main.py "<sentence>"     Seeds inputs from a natural-language sentence via
                                     nlp_parser.py, then interactively asks for anything
                                     that couldn't be confidently extracted.

Pipeline for every run:
    1. User Input Module      -> InvestorProfile               (utils.py, models.py)
    2. Recommendation Engine  -> {asset: percentage}            (recommendation_engine.py)
    3. Portfolio Allocator    -> [AllocationItem] with amounts  (portfolio_allocator.py)
    4. Explanation Module     -> explanation text per item      (explanations.py)
    5. Output Module          -> formatted report               (build_report, below)
"""

import sys
from decimal import Decimal

from .models import InvestorProfile, RiskTolerance, InvestmentGoal, PortfolioRecommendation
from .recommendation_engine import RecommendationEngine
from .portfolio_allocator import PortfolioAllocator
from .explanations import attach_explanations, explain_overall
from . import nlp_parser
from .rules import ASSET_DISPLAY_NAMES
from .utils import (
    ValidationError,
    validate_amount,
    validate_duration,
    validate_choice,
    format_currency,
    format_percentage,
)

RISK_ALIASES = {
    "1": "LOW", "low": "LOW", "l": "LOW",
    "2": "MEDIUM", "medium": "MEDIUM", "m": "MEDIUM", "med": "MEDIUM",
    "3": "HIGH", "high": "HIGH", "h": "HIGH",
}

GOAL_ALIASES = {
    "1": "CAPITAL_PRESERVATION", "capital preservation": "CAPITAL_PRESERVATION", "preservation": "CAPITAL_PRESERVATION",
    "2": "WEALTH_GROWTH", "wealth growth": "WEALTH_GROWTH", "growth": "WEALTH_GROWTH",
    "3": "PASSIVE_INCOME", "passive income": "PASSIVE_INCOME", "income": "PASSIVE_INCOME",
}


# ---------------------------------------------------------------------------
# 1. User Input Module
# ---------------------------------------------------------------------------

def collect_profile_interactively(seed: dict = None) -> InvestorProfile:
    """Prompts for each field, validating as it goes and handling bad input
    gracefully (re-prompting with a clear reason rather than crashing).

    If `seed` already has a usable value for a field (e.g. extracted by
    nlp_parser from a sentence the user typed), that value is offered as a
    default the user can accept by pressing Enter, or override by typing
    a new value.
    """
    seed = seed or {}

    amount = _collect_amount(seed.get("amount"))
    duration = _collect_duration(seed.get("duration_years"))
    risk = _collect_risk(seed.get("risk_tolerance"))
    goal = _collect_goal(seed.get("goal"))

    return InvestorProfile(
        amount=amount,
        duration_years=duration,
        risk_tolerance=RiskTolerance(risk),
        goal=InvestmentGoal(goal),
    )


def _collect_amount(default: Decimal = None) -> Decimal:
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"Investment amount{suffix}: ").strip()
        if not raw and default is not None:
            return default
        try:
            return validate_amount(raw)
        except ValidationError as exc:
            print(f"  -> Invalid input: {exc}\n")


def _collect_duration(default: Decimal = None) -> Decimal:
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"Investment duration in years{suffix}: ").strip()
        if not raw and default is not None:
            return default
        try:
            return validate_duration(raw)
        except ValidationError as exc:
            print(f"  -> Invalid input: {exc}\n")


def _collect_risk(default: str = None) -> str:
    suffix = f" [{default}]" if default else ""
    print("Risk tolerance: 1) Low  2) Medium  3) High")
    while True:
        raw = input(f"Choose risk tolerance{suffix}: ").strip()
        if not raw and default is not None:
            return default
        try:
            return validate_choice(raw, RISK_ALIASES, "risk tolerance")
        except ValidationError as exc:
            print(f"  -> Invalid input: {exc}\n")


def _collect_goal(default: str = None) -> str:
    suffix = f" [{default}]" if default else ""
    print("Investment goal: 1) Capital Preservation  2) Wealth Growth  3) Passive Income")
    while True:
        raw = input(f"Choose investment goal{suffix}: ").strip()
        if not raw and default is not None:
            return default
        try:
            return validate_choice(raw, GOAL_ALIASES, "investment goal")
        except ValidationError as exc:
            print(f"  -> Invalid input: {exc}\n")


# ---------------------------------------------------------------------------
# 5. Output Module
# ---------------------------------------------------------------------------

def build_report(recommendation: PortfolioRecommendation) -> str:
    """Formats a PortfolioRecommendation into a clear, plain-text report:
    allocation percentages, investment amounts, and the reasoning behind
    them (requirement 5)."""
    profile = recommendation.profile
    lines = []

    lines.append("=" * 64)
    lines.append("INVESTMENT PORTFOLIO RECOMMENDATION".center(64))
    lines.append("=" * 64)
    lines.append(f"Amount:          {format_currency(profile.amount)}")
    lines.append(f"Duration:        {profile.duration_years} years ({profile.duration_bucket()} term)")
    lines.append(f"Risk Tolerance:  {profile.risk_tolerance.value.title()}")
    lines.append(f"Goal:            {profile.goal.value.replace('_', ' ').title()}")
    lines.append("-" * 64)
    lines.append(f"{'Asset':<10}{'Allocation':>12}{'Amount':>22}")
    lines.append("-" * 64)

    for item in recommendation.items:
        name = ASSET_DISPLAY_NAMES[item.asset.value]
        lines.append(
            f"{name:<10}"
            f"{format_percentage(item.percentage):>12}"
            f"{format_currency(item.amount):>22}"
        )

    lines.append("-" * 64)
    lines.append(
        f"{'TOTAL':<10}"
        f"{format_percentage(recommendation.total_percentage()):>12}"
        f"{format_currency(recommendation.total_amount()):>22}"
    )
    lines.append("=" * 64)
    lines.append("WHY THIS ALLOCATION".center(64))
    lines.append("=" * 64)
    lines.append(explain_overall(profile))
    lines.append("")

    for item in recommendation.items:
        name = ASSET_DISPLAY_NAMES[item.asset.value]
        lines.append(f"* {name} ({format_percentage(item.percentage)}): {item.explanation}")

    lines.append("=" * 64)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Orchestration (steps 2-4 of the pipeline)
# ---------------------------------------------------------------------------

def build_recommendation(profile: InvestorProfile) -> PortfolioRecommendation:
    """Runs the Recommendation Engine, Portfolio Allocator, and Explanation
    Module for an already-validated profile."""
    engine = RecommendationEngine(profile)
    percentages = engine.generate_allocation()

    items = PortfolioAllocator.allocate(profile.amount, percentages)
    attach_explanations(items)

    recommendation = PortfolioRecommendation(profile=profile, items=items)
    recommendation.summary = explain_overall(profile)
    return recommendation


def run_demo():
    """Runs three illustrative profiles with no user interaction -- useful
    for quickly sanity-checking the engine end to end."""
    demo_profiles = [
        InvestorProfile(Decimal("50000"), Decimal("2"), RiskTolerance.LOW, InvestmentGoal.CAPITAL_PRESERVATION),
        InvestorProfile(Decimal("200000"), Decimal("5"), RiskTolerance.MEDIUM, InvestmentGoal.WEALTH_GROWTH),
        InvestorProfile(Decimal("1000000"), Decimal("15"), RiskTolerance.HIGH, InvestmentGoal.PASSIVE_INCOME),
    ]
    for profile in demo_profiles:
        recommendation = build_recommendation(profile)
        print(build_report(recommendation))
        print()


def run_interactive(seed: dict = None):
    profile = collect_profile_interactively(seed)
    recommendation = build_recommendation(profile)
    print()
    print(build_report(recommendation))


def main():
    args = sys.argv[1:]

    if args and args[0] == "--demo":
        run_demo()
        return

    seed = None
    if args:
        sentence = " ".join(args)
        seed = nlp_parser.parse(sentence)
        if seed:
            print(f"(Parsed from your sentence: {seed})\n")
        else:
            print("(Could not extract any fields from that sentence -- starting from scratch.)\n")

    run_interactive(seed)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n\nNo more input received -- exiting without a recommendation. Goodbye!")
