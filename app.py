from datetime import date
from functools import wraps
from pathlib import Path

import joblib

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from db import db, init_db
from models import User, Transaction

from api.routes import api_bp

from services.auth_service import (
    authenticate,
    create_user,
    logout_user,
)

from services.finance_service import (
    dashboard_context,
    money,
    totals,
)

from services.model_loader import load_models

from dashboard.analytics_dashboard import create_dashboard

app = Flask(__name__)

app.config["SECRET_KEY"] = "finwise-dev-secret"

init_db(app)

create_dashboard(app)

app.register_blueprint(api_bp)

load_models()



BASE_DIR = Path(__file__).resolve().parent

salary_metadata = joblib.load(
    BASE_DIR / "trained_models" / "salary_metadata.pkl"
)

education_levels = list(
    salary_metadata["education_mapping"].keys()
)

job_titles = salary_metadata["top_jobs"]


def current_user():

    user_id = session.get("user_id")

    if not user_id:
        return None

    return db.session.get(User, user_id)


def login_required(view):

    @wraps(view)
    def wrapper(*args, **kwargs):

        if current_user() is None:

            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapper


@app.context_processor
def inject_user():

    user = current_user()

    if user is None:

        return {
            "user": {
                "name": "Guest",
                "email": ""
            },
            "money": money
        }

    return {
        "user": user,
        "money": money
    }


@app.route("/")
def home():

    if current_user():

        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user = authenticate(

            request.form["email"],

            request.form["password"]

        )

        if user:

            return redirect(url_for("dashboard"))

        return render_template(

            "auth/login.html",

            page_title="Login",

            auth_page=True,

            auth_error="Invalid email or password."

        )

    return render_template(

        "auth/login.html",

        page_title="Login",

        auth_page=True

    )


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        if request.form["password"] != request.form["confirmPassword"]:

            return render_template(

                "auth/register.html",

                page_title="Register",

                auth_page=True,

                auth_error="Passwords do not match."

            )

        if User.query.filter_by(

            email=request.form["email"].strip().lower()

        ).first():

            return render_template(

                "auth/register.html",

                page_title="Register",

                auth_page=True,

                auth_error="Email already exists."

            )

        create_user(request.form)

        return redirect(url_for("login"))

    return render_template(

        "auth/register.html",

        page_title="Register",

        auth_page=True

    )


@app.route("/logout")
def logout():

    logout_user()

    return redirect(url_for("login"))


# ===========================
# Dashboard
# ===========================

@app.route("/dashboard")
@login_required
def dashboard():

    summary = dashboard_context(current_user())

    return render_template(

        "app/dashboard.html",

        page_title="Dashboard",

        active_page="dashboard",

        summary=summary,

        cash_flow_bars=summary["cash_flow_bars"]

    )


# ===========================
# Transactions
# ===========================

@app.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():

    user = current_user()

    if request.method == "POST":

        tx = Transaction(

            user_id=user.id,

            date=date.fromisoformat(
                request.form["date"]
            ),

            category=request.form["category"],

            note=request.form.get(
                "note",
                ""
            ),

            amount=abs(
                float(request.form["amount"])
            ),

            type=request.form["type"].lower(),

            currency=request.form.get(
                "currency",
                "USD"
            )

        )

        db.session.add(tx)

        db.session.commit()

        return redirect(
            url_for("transactions")
        )

    query = Transaction.query.filter_by(
        user_id=user.id
    )

    search = request.args.get(
        "q",
        ""
    ).strip()

    if search:

        query = query.filter(

            db.or_(

                Transaction.category.ilike(
                    f"%{search}%"
                ),

                Transaction.note.ilike(
                    f"%{search}%"
                )

            )

        )

    txs = query.order_by(

        Transaction.date.desc(),

        Transaction.id.desc()

    ).all()

    stats = totals(user)

    categories = [

        row[0]

        for row in

        db.session.query(
            Transaction.category
        )

        .filter_by(
            user_id=user.id
        )

        .distinct()

        .order_by(
            Transaction.category
        )

        .all()

        if row[0]

    ]

    return render_template(

        "app/transactions.html",

        page_title="Transactions",

        active_page="transactions",

        transactions=txs,

        total_inflow=money(
            stats["income"]
        ),

        total_outflow=money(
            stats["expenses"]
        ),

        net_change=money(
            stats["balance"]
        ),

        categories=categories

    )


@app.route(
    "/transactions/<int:transaction_id>/delete",
    methods=["POST"]
)
@login_required
def delete_transaction(transaction_id):

    tx = Transaction.query.filter_by(

        id=transaction_id,

        user_id=current_user().id

    ).first_or_404()

    db.session.delete(tx)

    db.session.commit()

    return redirect(
        url_for("transactions")
    )


# ===========================
# Predictions
# ===========================

@app.route("/predictions")
@login_required
def predictions():

    return render_template(

        "app/predictions.html",

        page_title="Prediction Center",

        active_page="predictions",

        education_levels=education_levels,

        job_titles=job_titles

    )


# ===========================
# Recommendation
# ===========================

@app.route("/recommendations")
@login_required
def recommendations():

    return render_template(
        "app/recommendations.html",
        page_title="Recommendations",
        active_page="recommendations",
    )


# ===========================
# Chatbot
# ===========================

@app.route("/chatbot")
@login_required
def chatbot():

    return render_template(

        "app/chatbot.html",

        page_title="AI Assistant",

        active_page="chatbot",

        conversation_history=[]

    )

# ===========================
# Reports
# ===========================

@app.route("/reports")
@login_required
def reports():

    user = current_user()

    summary = dashboard_context(user)

    stats = totals(user)

    return render_template(

        "app/reports.html",

        page_title="Reports",

        active_page="reports",

        summary=summary,

        income=money(
            stats["income"]
        ),

        expenses=money(
            stats["expenses"]
        ),

        balance=money(
            stats["balance"]
        ),

        savings=money(
            stats["savings"]
        ),

        category_breakdown=summary[
            "category_breakdown"
        ],

        cash_flow_bars=summary[
            "cash_flow_bars"
        ],

        financial_health="Live"

    )


# ===========================
# Profile
# ===========================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
@login_required
def profile():

    user = current_user()

    if request.method == "POST":

        user.name = request.form["name"]

        user.email = (
            request.form["email"]
            .strip()
            .lower()
        )

        user.age = int(
            request.form.get(
                "age",
                user.age or 0
            )
        )

        user.country = request.form.get(
            "country",
            ""
        )

        user.occupation_level = request.form.get(
            "occupation",
            ""
        )

        user.salary = float(
            request.form.get(
                "salary",
                0
            )
        )

        db.session.commit()

        return redirect(
            url_for("profile")
        )

    return render_template(

        "app/profile.html",

        page_title="Profile",

        active_page="profile",

        user=user

    )


# ===========================
# Analytics (Admin Only)
# ===========================

ADMIN_PASSWORD = "admin1234"


@app.route("/admin-login", methods=["GET", "POST"])
@login_required
def admin_login():

    if session.get("is_admin"):
        return redirect(url_for("analytics"))

    if request.method == "POST":

        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:

            session["is_admin"] = True

            return redirect(url_for("analytics"))

        Flask("Incorrect password.")

    return render_template(
        "app/admin_login.html",
        page_title="Analytics Login",
        active_page="analytics",
    )


@app.route("/analytics")
@login_required
def analytics():

    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    return render_template(
        "app/analytics.html",
        page_title="Analytics Dashboard",
        active_page="analytics",
    )


@app.route("/admin-logout")
@login_required
def admin_logout():

    session.pop("is_admin", None)

    return redirect(url_for("dashboard"))


# ===========================
# Run
# ===========================

if __name__ == "__main__":

    import os

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )