"""
utils.py
========
Shared, low-level helpers used across the Investment Recommendation System:

- Interactive input collection with validation and graceful error handling
  (the "User Input Module" from the spec).
- Duration bucketing (maps a number of years to Short / Medium / Long).
- "Largest remainder" rounding, used to turn fractional percentages and
  fractional money amounts into values that still sum to EXACTLY 100% /
  the original investment amount -- this is what guarantees requirement
  3 ("Ensure total allocation equals 100%") actually holds, instead of
  being approximately true after rounding.
- Simple currency/percentage formatting used by the output report.

Keeping these here (rather than duplicating rounding/validation logic in
recommendation_engine.py and portfolio_allocator.py) is what lets both of
those modules guarantee their outputs always add up correctly.
"""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Dict

from .rules import SHORT_MAX_YEARS, MEDIUM_MAX_YEARS


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class ValidationError(Exception):
    """Raised when a user-supplied value fails validation. Carries a
    human-readable message that is safe to show directly to the user."""


def validate_amount(raw_value: str) -> Decimal:
    """Parse and validate an investment amount.

    Accepts plain numbers and numbers with thousands separators or simple
    currency markers (e.g. "100,000", "$100000", "100000 EGP").
    Raises ValidationError on anything that isn't a sane positive number.
    """
    if raw_value is None:
        raise ValidationError("Investment amount is required.")

    cleaned = (
        raw_value.strip()
        .replace(",", "")
        .replace("$", "")
        .replace("EGP", "")
        .replace("egp", "")
        .strip()
    )
    if not cleaned:
        raise ValidationError("Investment amount cannot be empty.")

    try:
        amount = Decimal(cleaned)
    except InvalidOperation:
        raise ValidationError(f"'{raw_value}' is not a valid number.")

    if amount <= 0:
        raise ValidationError("Investment amount must be greater than zero.")
    if amount > Decimal("1000000000000"):
        raise ValidationError("Investment amount is unrealistically large -- please check it.")

    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def validate_duration(raw_value: str) -> Decimal:
    """Parse and validate an investment duration, in years. Fractional
    years (e.g. "2.5") are allowed."""
    if raw_value is None:
        raise ValidationError("Investment duration is required.")

    cleaned = (
        raw_value.strip()
        .lower()
        .replace("years", "")
        .replace("year", "")
        .replace("yrs", "")
        .replace("yr", "")
        .strip()
    )
    if not cleaned:
        raise ValidationError("Investment duration cannot be empty.")

    try:
        duration = Decimal(cleaned)
    except InvalidOperation:
        raise ValidationError(f"'{raw_value}' is not a valid duration.")

    if duration <= 0:
        raise ValidationError("Investment duration must be greater than zero years.")
    if duration > 100:
        raise ValidationError("Investment duration must be 100 years or fewer.")

    return duration


def validate_choice(raw_value: str, valid_values: Dict[str, str], field_name: str) -> str:
    """Normalize free-text input against a set of acceptable aliases.

    `valid_values` maps every acceptable lowercase alias to its canonical
    value, e.g. {"1": "LOW", "low": "LOW", "l": "LOW", ...}.
    """
    if raw_value is None:
        raise ValidationError(f"{field_name} is required.")

    key = raw_value.strip().lower()
    if key not in valid_values:
        raise ValidationError(
            f"'{raw_value}' is not a recognized {field_name}. "
            f"Valid options: {sorted(set(valid_values.values()))}."
        )
    return valid_values[key]


# ---------------------------------------------------------------------------
# Duration bucketing
# ---------------------------------------------------------------------------

def classify_duration(years: Decimal) -> str:
    """Map a number of years onto the SHORT / MEDIUM / LONG bucket used by
    the rule tables in rules.py."""
    if years <= SHORT_MAX_YEARS:
        return "SHORT"
    if years <= MEDIUM_MAX_YEARS:
        return "MEDIUM"
    return "LONG"


# ---------------------------------------------------------------------------
# Largest-remainder rounding (a.k.a. Hamilton's method)
# ---------------------------------------------------------------------------

def distribute_exact(total: Decimal, weights: Dict[str, Decimal], places: str = "0.01") -> Dict[str, Decimal]:
    """
    Split `total` across the keys of `weights`, proportionally to their
    weights, rounding every share to `places`, while guaranteeing the
    shares sum to EXACTLY `total` (no cent -- or percentage point -- lost
    or gained to rounding).

    Used twice in the system:
      1. recommendation_engine.py -- splitting 100(%) across asset classes.
      2. portfolio_allocator.py   -- splitting the investment amount across
         asset classes.

    Algorithm (largest remainder / Hamilton's method):
      - Give every key its rounded ("floor") share.
      - Hand out (or claw back) the few leftover quantum-units, one at a
        time, to the keys whose rounding lost (or gained) the most,
        until the total matches exactly.
    """
    quantum = Decimal(places)
    weight_total = sum(weights.values())
    if weight_total == 0:
        raise ValueError("Cannot distribute a total across all-zero weights.")

    raw_shares = {key: (total * weight / weight_total) for key, weight in weights.items()}
    rounded_shares = {key: value.quantize(quantum, rounding=ROUND_HALF_UP) for key, value in raw_shares.items()}

    distributed_total = sum(rounded_shares.values())
    remainder_units = int((total - distributed_total) / quantum)

    if remainder_units != 0:
        # Rank keys by how much their rounded share differs from their raw
        # share, and adjust the biggest "losers" (or "winners") first.
        ordered_keys = sorted(
            weights.keys(),
            key=lambda k: (raw_shares[k] - rounded_shares[k]),
            reverse=remainder_units > 0,
        )
        step = quantum if remainder_units > 0 else -quantum
        for key in ordered_keys[: abs(remainder_units)]:
            rounded_shares[key] += step

    return rounded_shares


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_currency(amount: Decimal, currency: str = "EGP") -> str:
    """Format a Decimal amount with thousands separators, e.g. '12,345.00 EGP'."""
    return f"{amount:,.2f} {currency}"


def format_percentage(pct: Decimal) -> str:
    return f"{pct:.2f}%"
