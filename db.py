from pathlib import Path

import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "instance"
DATABASE_PATH = DATABASE_DIR / "finwise.db"
SCHEMA_PATH = BASE_DIR / "dataBase" / "schema.sql"
USERS_XLSX = BASE_DIR / "dataBase" / "users_data.xlsx"
TRANSACTIONS_XLSX = BASE_DIR / "dataBase" / "transactions_data.xlsx"


def init_db(app):
    DATABASE_DIR.mkdir(exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        _apply_schema()
        _seed_from_excel()


def _apply_schema():
    _rebuild_if_schema_is_stale()
    statements = [
        statement.strip()
        for statement in SCHEMA_PATH.read_text(encoding="utf-8").split(";")
        if statement.strip()
    ]
    connection = db.session.connection()
    for statement in statements:
        connection.execute(text(statement))
    db.session.commit()


def _rebuild_if_schema_is_stale():
    connection = db.session.connection()
    expected = {
        "users": {
            "id",
            "name",
            "email",
            "password_hash",
            "age",
            "country",
            "occupation_level",
            "salary",
            "created_at",
        },
        "transactions": {
            "id",
            "user_id",
            "date",
            "category",
            "note",
            "amount",
            "type",
            "currency",
            "created_at",
        },
    }
    for table, columns in expected.items():
        existing = {
            row[1]
            for row in connection.execute(text(f"PRAGMA table_info({table})")).fetchall()
        }
        if existing and not columns.issubset(existing):
            connection.execute(text("DROP TABLE IF EXISTS transactions"))
            connection.execute(text("DROP TABLE IF EXISTS users"))
            db.session.commit()
            return


def _seed_from_excel():
    user_count = db.session.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
    tx_count = db.session.execute(text("SELECT COUNT(*) FROM transactions")).scalar() or 0

    if user_count == 0:
        users = pd.read_excel(USERS_XLSX, header=1).dropna(how="all")
        for _, row in users.iterrows():
            db.session.execute(
                text(
                    """
                    INSERT INTO users
                    (id, name, email, password_hash, age, country, occupation_level, salary)
                    VALUES
                    (:id, :name, :email, :password_hash, :age, :country, :occupation_level, :salary)
                    """
                ),
                {
                    "id": _int(row.get("ID")),
                    "name": str(row.get("Name", "")).strip(),
                    "email": str(row.get("Email", "")).strip().lower(),
                    "password_hash": generate_password_hash(str(row.get("Password", ""))),
                    "age": _int(row.get("Age")),
                    "country": "Egypt",
                    "occupation_level": str(row.get("Occupation Level", "")).strip(),
                    "salary": _float(row.get("Annual Salary")),
                },
            )

    if tx_count == 0:
        transactions = pd.read_excel(TRANSACTIONS_XLSX, header=1).dropna(how="all")
        for _, row in transactions.iterrows():
            db.session.execute(
                text(
                    """
                    INSERT INTO transactions
                    (id, user_id, date, category, note, amount, type, currency)
                    VALUES
                    (:id, :user_id, :date, :category, :note, :amount, :type, :currency)
                    """
                ),
                {
                    "id": _int(row.get("ID")),
                    "user_id": _int(row.get("User ID")),
                    "date": pd.to_datetime(row.get("Date")).date().isoformat(),
                    "category": str(row.get("Category", "Other")).strip() or "Other",
                    "note": str(row.get("Note", "")).strip(),
                    "amount": abs(_float(row.get("Amount"))),
                    "type": str(row.get("Type", "expense")).strip().lower(),
                    "currency": str(row.get("Currency", "USD")).strip() or "USD",
                },
            )

    db.session.commit()


def _int(value):
    if pd.isna(value):
        return None
    return int(value)


def _float(value):
    if pd.isna(value):
        return 0.0
    return float(value)
