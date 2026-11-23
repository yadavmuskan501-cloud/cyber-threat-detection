
import json
from pathlib import Path

import pandas as pd

from predict import load_model, predict_threat


DATASET_PATH = Path(
    r"C:\Users\Dell\Downloads\archive (2)\combine.csv"
)

artifact = load_model()
feature_names = artifact["features"]

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
