
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Our verified CICIDS2017 dataset
DATASET_PATH = Path(
    r"C:\Users\Dell\Downloads\archive (2)\combine.csv"
)

RANDOM_STATE = 42
SAMPLE_SIZE = 200_000
CHUNK_SIZE = 50_000


def load_sample():
    """Read the large CSV in small batches to save RAM."""
    samples = []
    total_rows = 0

    for chunk in pd.read_csv(
        DATASET_PATH,
        chunksize=CHUNK_SIZE,
        low_memory=False
    ):
        chunk.columns = chunk.columns.str.strip()

        # Remove records with missing attack labels
        chunk = chunk.dropna(subset=["Label"]).copy()
        chunk["Label"] = chunk["Label"].astype(str).str.strip()
        chunk = chunk[chunk["Label"] != ""]

        total_rows += len(chunk)

        # Random sample from each chunk
        fraction = min(1.0, SAMPLE_SIZE / 2_214_469)

        sampled = chunk.sample(
            frac=fraction,
            random_state=RANDOM_STATE
        )
        samples.append(sampled)

    df = pd.concat(samples, ignore_index=True)

    print("Valid records scanned:", total_rows)
    print("Sampled records:", len(df))

    return df


def preprocess_data():
    df = load_sample()

    # Binary classification:
    # BENIGN = 0, any attack = 1
    y = (df["Label"] != "BENIGN").astype(int)

    X = df.drop(columns=["Label"])

    # Convert feature values to numbers
    X = X.apply(pd.to_numeric, errors="coerce")

    # Replace infinite values with missing values
    X = X.replace([np.inf, -np.inf], np.nan)

    # Use float32 to reduce RAM consumption
    X = X.astype("float32")

    # Split before fitting any imputer or model
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
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


if __name__ == "__main__":
    preprocess_data()
