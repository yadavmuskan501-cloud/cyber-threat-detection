
from pathlib import Path

import joblib
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

from preprocess import preprocess_data


def train_model():
    print("Loading and preprocessing dataset...")

    # Step 1: Load training and testing data
    X_train, X_test, y_train, y_test = preprocess_data()

    # Save feature names BEFORE converting DataFrames to arrays
    feature_names = X_train.columns.tolist()

    print("\nHandling missing values...")

    # Step 2: Replace missing values using training data only
    imputer = SimpleImputer(
        strategy="median",
        keep_empty_features=True
    )

    X_train = imputer.fit_transform(X_train)
    X_test = imputer.transform(X_test)

    # Reduce memory usage
    X_train = X_train.astype(np.float32)
    X_test = X_test.astype(np.float32)

    print("\nTraining Random Forest model...")

    # Step 3: Create Random Forest classifier
    model = RandomForestClassifier(
        n_estimators=50,
        max_depth=15,
        random_state=42,
        n_jobs=2,
        class_weight="balanced"
    )

    # Step 4: Train model
    model.fit(X_train, y_train)

    print("\nEvaluating model...")

    # Step 5: Predict testing data
    y_pred = model.predict(X_test)

    # Step 6: Calculate performance metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(
        y_test, y_pred, zero_division=0
    )
    recall = recall_score(
        y_test, y_pred, zero_division=0
    )
    f1 = f1_score(
        y_test, y_pred, zero_division=0
    )

    print("\n========== MODEL PERFORMANCE ==========")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

    print("\n========== CLASSIFICATION REPORT ==========")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=["BENIGN", "ATTACK"],
            zero_division=0
        )
    )

    print("\n========== CONFUSION MATRIX ==========")
    print(confusion_matrix(y_test, y_pred))

    # Step 7: Create model directory
    model_dir = Path(__file__).resolve().parent / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "random_forest_model.pkl"

    # Step 8: Save model, imputer and feature names
    artifact = {
        "model": model,
        "imputer": imputer,
        "features": feature_names,
        "label_mapping": {
            0: "BENIGN",
            1: "ATTACK"
        },
    }

    joblib.dump(
        artifact,
        model_path,
        compress=3
    )

    print("\n========== TRAINING COMPLETED ==========")
    print("Model saved successfully!")
    print("Model location:", model_path)


if __name__ == "__main__":
    train_model()
