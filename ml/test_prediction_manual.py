
import os
import json
from pathlib import Path

import pandas as pd

from predict import load_model, predict_threat


# Dataset path: defaults to the current user's Downloads folder.
# Teammates can override it using the DATASET_PATH environment variable.
DATASET_PATH = Path(
    os.getenv(
        "DATASET_PATH",
        str(Path.home() / "Downloads" / "combine.csv")
    )
)

artifact = load_model()
feature_names = artifact["features"]

# Check whether the dataset exists
if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}\n"
        "Place combine.csv in your Downloads folder or set DATASET_PATH."
    )

# Read one actual dataset record
sample = pd.read_csv(DATASET_PATH, nrows=1)
sample.columns = sample.columns.str.strip()

features = {}

for feature in feature_names:
    value = pd.to_numeric(
        sample[feature].iloc[0],
        errors="coerce"
    )

    features[feature] = (
        float(value) if pd.notna(value) else None
    )

# Save Swagger-compatible request body
request_body = {"features": features}

output_path = Path(__file__).resolve().parent / "sample_request.json"

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(request_body, file, indent=2, allow_nan=False)

print("Sample request created successfully!")
print("Total features:", len(features))
print("Saved to:", output_path)

# Test ML prediction directly
result = predict_threat(features)

print("\nML Prediction Result:")
print(json.dumps(result, indent=2))
