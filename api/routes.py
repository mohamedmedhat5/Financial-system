from flask import Blueprint, jsonify, request

from flask import session
from models import User

from services.predictions import (
    predict_recommendation,
    predict_salary,
    predict_expense,
    predict_cost,
    predict_inflation,
)

from services.preprocessing import (
    PreprocessingError,
)

from services.finance_service import (
    totals,
    category_breakdown,
    user_transactions,
)

from services.ai_assistant import assistant

api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api",
)

def handle_prediction(func):

    try:

        if not request.is_json:
            return jsonify({
                "error": "Request must be JSON."
            }), 400

        payload = request.get_json()
        if payload is None:

            return jsonify({
                "error": "Empty request body."
            }), 400

        result = func(payload)

        return jsonify(result), 200

    except PreprocessingError as e:

        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
    


def build_user_context(user):

    stats = totals(user)

    categories = category_breakdown(user)

    recent = user_transactions(user)[:5]

    top_categories = ""

    for name, amount in sorted(
        categories.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]:

        top_categories += f"- {name}: ${amount}\n"

    recent_transactions = ""

    for tx in recent:

        recent_transactions += (
            f"- {tx.date} | "
            f"{tx.category} | "
            f"{tx.type} | "
            f"${tx.amount}\n"
        )

    context = f"""
User Profile

Name: {user.name}
Age: {user.age}
Country: {user.country}
Occupation: {user.occupation_level}
Current Salary: ${user.salary}

Financial Summary

Income: ${stats['income']}
Expenses: ${stats['expenses']}
Balance: ${stats['balance']}
Savings: ${stats['savings']}

Top Expense Categories

{top_categories}

Recent Transactions

{recent_transactions}
"""

    return context


@api_bp.post("/predict-salary")
def predict_salary_endpoint():

    return handle_prediction(
        predict_salary
    )


@api_bp.post("/predict-expense")
def predict_expense_endpoint():

    return handle_prediction(
        predict_expense
    )


@api_bp.post("/predict-cost-living")
def predict_cost_endpoint():

    return handle_prediction(
        predict_cost
    )


@api_bp.post("/predict-inflation")
def predict_inflation_endpoint():

    return handle_prediction(
        predict_inflation
    )

@api_bp.post("/recommendation")
def predict_recommendation_endpoint():

    return handle_prediction(
        predict_recommendation
    )

@api_bp.post("/chat")
def chat_endpoint():

    try:

        if not request.is_json:
            return jsonify({
                "error": "Request must be JSON."
            }), 400

        payload = request.get_json()

        message = payload.get("message", "").strip()

        if not message:
            return jsonify({
                "error": "Message is required."
            }), 400

        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user = User.query.get(user_id)

        context = build_user_context(user)

        reply = assistant.chat(
        message,
        context
        )

        return jsonify({

            "reply": reply

        })

    except Exception as e:

        return jsonify({

            "error": str(e)

        }), 500