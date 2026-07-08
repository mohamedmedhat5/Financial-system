from decimal import Decimal, InvalidOperation

import pandas as pd

from services.model_loader import (
    get_metadata,
    get_scaler,
)


class PreprocessingError(ValueError):
    pass


def require_fields(payload, fields):

    missing = [
        field
        for field in fields
        if field not in payload
    ]

    if missing:
        raise PreprocessingError(
            f"Missing fields: {', '.join(missing)}"
        )


def parse_decimal(value, name):

    try:
        return Decimal(str(value))

    except (InvalidOperation, TypeError):

        raise PreprocessingError(
            f"{name} is invalid."
        )


def serialize_prediction(prediction):

    value = prediction[0] if hasattr(
        prediction,
        "__len__"
    ) else prediction

    if hasattr(value, "item"):
        value = value.item()

    return value

def preprocess_salary(payload):

    metadata = get_metadata("salary")

    scaler = get_scaler("salary")

    require_fields(
        payload,
        (
            "age",
            "gender",
            "education_level",
            "job_title",
            "years_of_experience",
        ),
    )

    age = float(payload["age"])

    exp = float(payload["years_of_experience"])

    job = payload["job_title"].lower().strip()

    if job not in metadata["top_jobs"]:
        job = "other"

    education = metadata["education_mapping"][
        payload["education_level"].lower().strip()
    ]

    if exp < 3:
        seniority = metadata["seniority_mapping"]["junior"]

    elif exp < 10:
        seniority = metadata["seniority_mapping"]["mid"]

    else:
        seniority = metadata["seniority_mapping"]["senior"]

    if age < 30:
        age_group = "junior"

    elif age < 45:
        age_group = "mid_age"

    else:
        age_group = "senior"

    df = pd.DataFrame([{

        "age": age,

        "gender": payload["gender"].lower().strip(),

        "education_level": education,

        "job_title": job,

        "years_of_experience": exp,

        "experience_per_age":
            exp / age if age else 0,

        "seniority": seniority,

        "age_group": age_group

    }])

    df = pd.get_dummies(df)

    df = df.reindex(

        columns=metadata["feature_columns"],

        fill_value=0

    )

    if metadata["scaled"]:

        df = scaler.transform(df)

    return df

def preprocess_expense(payload):

    require_fields(
        payload,
        (
            "year",
            "month",
            "income",
            "income_bracket",
            "festival",
            "festival_count",
        ),
    )

    return pd.DataFrame([{

        "Year": int(payload["year"]),

        "Month": int(payload["month"]),

        "Income": float(payload["income"]),

        "Income_Bracket": payload["income_bracket"],

        "Festivals": payload["festival"],

        "Festival_Count": int(payload["festival_count"])

    }])


def preprocess_cost(payload):

    require_fields(
        payload,
        (
            "cost_of_living_index",
            "rent_index",
            "cost_of_living_plus_rent_index",
            "groceries_index",
            "restaurant_price_index",
            "local_purchasing_power_index",
            "income_to_cost_ratio",
        ),
    )

    return pd.DataFrame([{

        "Cost of Living Index":
            float(payload["cost_of_living_index"]),

        "Rent Index":
            float(payload["rent_index"]),

        "Cost of Living Plus Rent Index":
            float(payload["cost_of_living_plus_rent_index"]),

        "Groceries Index":
            float(payload["groceries_index"]),

        "Restaurant Price Index":
            float(payload["restaurant_price_index"]),

        "Local Purchasing Power Index":
            float(payload["local_purchasing_power_index"]),

        "Income_to_Cost_Ratio":
            float(payload["income_to_cost_ratio"])

    }])


def preprocess_inflation(payload):

    require_fields(
        payload,
        (
            "lag_1",
            "lag_2",
            "lag_3",
        ),
    )

    return pd.DataFrame([{
        "lag_1": float(payload["lag_1"]),
        "lag_2": float(payload["lag_2"]),
        "lag_3": float(payload["lag_3"]),
        "rolling_mean_3": float(payload["rolling_mean_3"]),
        "rolling_std_3": float(payload["rolling_std_3"]),
    }])