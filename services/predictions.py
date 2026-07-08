from services.model_loader import (
    predict_with_model,
)

from services.preprocessing import (
    preprocess_salary,
    preprocess_expense,
    preprocess_cost,
    preprocess_inflation,
    serialize_prediction,
)

from services.recommendation import recommend


def predict_salary(payload):

    X = preprocess_salary(payload)

    prediction = predict_with_model(
        "salary",
        X
    )

    return {
        "prediction": round(
            serialize_prediction(prediction),
            2
        )
    }


def predict_expense(payload):

    X = preprocess_expense(payload)

    prediction = predict_with_model(
        "expense",
        X
    )

    return {
        "prediction": round(
            serialize_prediction(prediction),
            2
        )
    }

def predict_cost(payload):

    X = preprocess_cost(payload)

    prediction = predict_with_model(
        "cost",
        X
    )

    return {
        "prediction": round(
            serialize_prediction(prediction),
            2
        )
    }


def predict_inflation(payload):

    X = preprocess_inflation(payload)

    prediction = predict_with_model(
        "inflation",
        X
    )

    return {
        "prediction": round(
            serialize_prediction(prediction),
            2
        )
    }

def predict_recommendation(payload):

    recommendation = recommend(payload)

    items = []

    for item in recommendation.items:

        items.append({

            "asset": item.asset.value,

            "percentage": float(item.percentage),

            "amount": float(item.amount),

            "explanation": item.explanation

        })

    return {

        "summary": recommendation.summary,

        "allocation": items

    }