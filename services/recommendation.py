from decimal import Decimal

from investment_recommender.models import (
    InvestorProfile,
    RiskTolerance,
    InvestmentGoal,
)

from investment_recommender.main import (
    build_recommendation,
)


def recommend(payload):

    profile = InvestorProfile(

        amount=Decimal(str(payload["amount"])),

        duration_years=Decimal(
            str(payload["duration_years"])
        ),

        risk_tolerance=RiskTolerance(
            payload["risk_tolerance"].upper()
        ),

        goal=InvestmentGoal(
            payload["goal"].upper()
        )

    )

    recommendation = build_recommendation(
        profile
    )

    return recommendation