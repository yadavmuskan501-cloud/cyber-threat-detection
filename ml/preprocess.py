
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


# ==========================================
# STEP 1: DATASET CONFIGURATION
# ==========================================

DATASET_PATH = Path(
    r"C:\Users\Dell\Downloads\archive (2)\combine.csv"
)

RANDOM_STATE = 42
SAMPLE_SIZE = 200_000
CHUNK_SIZE = 50_000


# ==========================================
# STEP 2: LOAD DATASET
# ==========================================

def load_sample():
    """Read the large CSV in chunks to reduce RAM usage."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    samples = []
    total_rows = 0

    for chunk_number, chunk in enumerate(
        pd.read_csv(
            DATASET_PATH,
            chunksize=CHUNK_SIZE,
            low_memory=False
        )
    ):
        # Clean column names
        chunk.columns = chunk.columns.str.strip()

        # Remove missing labels
        chunk = chunk.dropna(subset=["Label"]).copy()

        # Clean label text
        chunk["Label"] = (
            chunk["Label"].astype(str).str.strip()
        )

        chunk = chunk[
            (chunk["Label"] != "") &
            (chunk["Label"].str.lower() != "nan")
        ]

        total_rows += len(chunk)

        # Sample approximately 200,000 records
        fraction = min(
            1.0,
            SAMPLE_SIZE / 2_214_469
        )

        sampled = chunk.sample(
            frac=fraction,
            random_state=RANDOM_STATE + chunk_number
        )

        samples.append(sampled)

    df = pd.concat(samples, ignore_index=True)

    print("Valid records scanned:", total_rows)
    print("Sampled records:", len(df))

    return df


# ==========================================
# STEP 3: PREPROCESS DATA
# ==========================================

def preprocess_data():

    df = load_sample()

    # Remove exact duplicate records
    before = len(df)

    df = df.drop_duplicates().reset_index(drop=True)

    print(
        "\nDuplicate records removed:",
        before - len(df)
    )

    print("Unique records remaining:", len(df))

    # Binary labels:
    # BENIGN = 0
    # ATTACK = 1
    y = (df["Label"] != "BENIGN").astype(int)

    # Separate features
    X = df.drop(columns=["Label"])

    # Convert features to numeric
    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )

    # Replace infinity with missing values
    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # Reduce RAM usage
    X = X.astype(np.float32)

    # ==========================================
    # STEP 4: REMOVE DUPLICATES AFTER CLEANING
    # ==========================================

    combined = X.copy()
    combined["Label"] = y.to_numpy()

    before_cleaning = len(combined)

    combined = (
        combined.drop_duplicates()
        .reset_index(drop=True)
    )

    print(
        "Additional duplicates removed:",
        before_cleaning - len(combined)
    )

    y = combined.pop("Label").astype(int)
    X = combined

    # ==========================================
    # STEP 5: HANDLE CONFLICTING LABELS
    # ==========================================

    # Identify feature-identical records
    # even when their labels are different.
    # Remove all ambiguous feature groups rather
    # than arbitrarily choosing one label.

    before_feature_dedup = len(X)

    conflicting_mask = X.duplicated(
        keep=False
    )

    conflicting_count = int(
        conflicting_mask.sum()
    )

    # All feature duplicates remaining at this
    # stage have different binary labels,
    # because exact feature-label duplicates
    # were removed above.
    X = X.loc[
        ~conflicting_mask
    ].reset_index(drop=True)

    y = y.loc[
        ~conflicting_mask
    ].reset_index(drop=True)

    print(
        "Ambiguous feature records removed:",
        conflicting_count
    )

    print(
        "Unique feature records remaining:",
        len(X)
    )

    # ==========================================
    # STEP 6: TRAIN-TEST SPLIT
    # ==========================================

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y
    )

    print("\nTraining records:", len(X_train))
    print("Testing records:", len(X_test))
    print("Features:", X.shape[1])

    print("\nTraining labels:")
    print(y_train.value_counts())

    print("\nTesting labels:")
    print(y_test.value_counts())

    return X_train, X_test, y_train, y_test


# ==========================================
# STEP 7: RUN PREPROCESSING
# ==========================================

if __name__ == "__main__":
    preprocess_data()
