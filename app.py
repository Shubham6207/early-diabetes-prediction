import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MODEL_PATH = os.environ.get("MODEL_PATH", "models/diabetes_model.joblib")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Run python train_model.py first.")

package = joblib.load(MODEL_PATH)
model = package["model"]
features = package["features"]

@app.get("/")
def home():
    return jsonify({"message": "Diabetes Prediction API is running"})

@app.post("/predict")
def predict():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Send a JSON object."}), 400
    try:
        values = {}
        for feature in features:
            value = float(data[feature])
            if not pd.notna(value) or value < 0:
                raise ValueError
            values[feature] = value
        patient = pd.DataFrame([values], columns=features)
        prediction = int(model.predict(patient)[0])
        probability = float(model.predict_proba(patient)[0][1])
        return jsonify({
            "success": True,
            "prediction": prediction,
            "probability": round(probability * 100, 2),
            "label": "Diabetes-positive class" if prediction == 1 else "Diabetes-negative class",
            "disclaimer": "Educational estimate only; not a medical diagnosis."
        })
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Provide all eight features as valid non-negative numbers."}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
