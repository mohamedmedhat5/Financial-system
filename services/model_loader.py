from pathlib import Path
from threading import Lock

import joblib

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_FILES = {
    "salary": {
        "model": "salary_model.pkl",
        "metadata": "salary_metadata.pkl",
        "scaler": "salary_scaler.pkl",
    },
    "expense": {
        "model": "expense_model.pkl",
        "metadata": "expense_metadata.pkl",
    },
    "cost": {
        "model": "costOfLiving_model.pkl",
        "metadata": "cost_metadata.pkl",
    },
    "inflation": {
        "model": "inflation_model.pkl",
        "metadata": "inflation_metadata.pkl",
    },
}

_loaded = False
_lock = Lock()

_models = {}
_metadata = {}
_scalers = {}


class ModelLoadError(RuntimeError):
    pass


def load_models():

    global _loaded

    with _lock:

        if _loaded:
            return

        for name, files in MODEL_FILES.items():

            try:

                _models[name] = joblib.load(
                    BASE_DIR / "trained_models" / files["model"]
                )

                if "metadata" in files:
                    _metadata[name] = joblib.load(
                        BASE_DIR / "trained_models" / files["metadata"]
                    )

                if "scaler" in files:
                    _scalers[name] = joblib.load(
                        BASE_DIR / "trained_models" / files["scaler"]
                    )

            except Exception as e:

                raise ModelLoadError(
                    f"Failed loading {name}: {e}"
                )

        _loaded = True


def get_model(name):

    load_models()

    return _models[name]


def get_metadata(name):

    load_models()

    return _metadata.get(name)


def get_scaler(name):

    load_models()

    return _scalers.get(name)


def predict_with_model(name, X):

    model = get_model(name)

    return model.predict(X)