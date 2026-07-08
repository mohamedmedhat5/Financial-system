from collections import defaultdict
from decimal import Decimal

from models import Transaction


def money(value):

    return f"${Decimal(value or 0):,.2f}"


def user_transactions(user):

    return (
        Transaction.query
        .filter_by(user_id=user.id)
        .order_by(
            Transaction.date.desc(),
            Transaction.id.desc()
        )
        .all()
    )


def totals(user):

    income = Decimal("0")

    expenses = Decimal("0")

    for tx in user_transactions(user):

        amount = Decimal(str(tx.amount))

        if tx.type == "income":

            income += amount

        else:

            expenses += amount

    return {

        "income": income,

        "expenses": expenses,

        "balance": income - expenses,

        "savings": income - expenses,

    }


def category_breakdown(user):

    result = defaultdict(Decimal)

    for tx in user_transactions(user):

        if tx.type == "expense":

            result[tx.category] += Decimal(str(tx.amount))

    return dict(result)


def cash_flow_bars(user):

    monthly = defaultdict(Decimal)

    for tx in user_transactions(user):

        amount = Decimal(str(tx.amount))

        if tx.type == "income":

            monthly[tx.date.strftime("%Y-%m")] += amount

        else:

            monthly[tx.date.strftime("%Y-%m")] -= amount

    values = [abs(monthly[key]) for key in sorted(monthly)[-12:]]

    if not values:

        return ""

    maximum = max(values)

    if maximum == 0:

        return ",".join("0" for _ in values)

    return ",".join(str(max(4, round((value / maximum) * 100))) for value in values)


def dashboard_context(user):

    t = totals(user)

    recent = user_transactions(user)[:10]

    breakdown = category_breakdown(user)

    return {

        "current_balance": money(t["balance"]),

        "income": money(t["income"]),

        "expenses": money(t["expenses"]),

        "savings": money(t["savings"]),

        "recent_transactions": recent,

        "category_breakdown": breakdown,

        "cash_flow_bars": cash_flow_bars(user),

    }
