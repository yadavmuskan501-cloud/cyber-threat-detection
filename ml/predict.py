
from pathlib import Path
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "random_forest_model.pkl"
)


@lru_cache(maxsize=1)
def load_model():
    """Load the trained model and preprocessing artifacts."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained ML model not found: {MODEL_PATH}"
        )

    artifact = joblib.load(MODEL_PATH)

    required_keys = {"model", "imputer", "features"}

    if not required_keys.issubset(artifact):
        raise ValueError(
            "Model artifact is missing required components."
        )

    return artifact


def predict_threat(features: dict):
    """Predict BENIGN or ATTACK from network traffic features."""

    artifact = load_model()

    model = artifact["model"]
    imputer = artifact["imputer"]
    feature_names = artifact["features"]

    # Reject unknown feature names
    unknown_features = set(features) - set(feature_names)

    if unknown_features:
        raise ValueError(
            f"Unknown features: {sorted(unknown_features)}"
        )

    # Ensure all required features are provided
    missing_features = set(feature_names) - set(features)

    if missing_features:
        raise ValueError(
            f"Missing features: {sorted(missing_features)}"
        )

    # Preserve the exact feature order used during training
    data = pd.DataFrame(
        [features],
        columns=feature_names
    )

    data = data.apply(
        pd.to_numeric,
        errors="coerce"
    )

    data = data.replace(
        [np.inf, -np.inf],
        np.nan
    ).astype(np.float32)

    # Apply the imputer fitted during training
    processed_data = imputer.transform(data)

    prediction_code = int(
        model.predict(processed_data)[0]
    )

    probabilities = model.predict_proba(processed_data)[0]

    class_index = list(model.classes_).index(prediction_code)

    confidence = float(probabilities[class_index])

    prediction = (
        "ATTACK" if prediction_code == 1 else "BENIGN"
    )

    return {
        "prediction": prediction,
        "prediction_code": prediction_code,
        "confidence": round(confidence, 4)
    }
