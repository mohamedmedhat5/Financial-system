SUPPORTED_CURRENCIES = {"USD"}
DEFAULT_CURRENCY = "USD"


def normalize_currency(currency):
    value = (currency or DEFAULT_CURRENCY).upper()
    if value not in SUPPORTED_CURRENCIES:
        raise ValueError("Only USD is supported.")
    return value
