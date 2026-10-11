import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score

DATA_URL = "https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv"
MODEL_PATH = "models/diabetes_model.joblib"

FEATURES = [
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age",
]

def main():
    os.makedirs("models", exist_ok=True)
    df = pd.read_csv(DATA_URL).drop_duplicates()
    df = df.dropna(subset=["Outcome"])
    df = df[df["Outcome"].isin([0, 1])].copy()

    X = df[FEATURES].copy()
    y = df["Outcome"].astype(int)

    for col in ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]:
        X.loc[X[col] == 0, col] = float("nan")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(
            n_estimators=200, class_weight="balanced", random_state=42
        )),
    ])
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    print(f"Accuracy: {accuracy_score(y_test, predictions):.4f}")
    print(f"ROC-AUC: {roc_auc_score(y_test, probabilities):.4f}")

    joblib.dump({"model": model, "features": FEATURES}, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    main()
