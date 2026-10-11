# Early Diabetes Prediction Website

GlycoSight is an educational diabetes-risk prediction project. The original responsive website is retained, with a Flask backend, SQLite signup/login, password show/hide controls, logout, and a scikit-learn prediction endpoint.

This project is for learning only and is not a medical diagnosis.

## Features

- Original GlycoSight landing page and prediction form
- SQLite-backed signup, login, and logout
- Password hashing and show/hide password controls
- Login-protected site and prediction endpoint
- Flask API using a saved scikit-learn model
- Model training script and evaluation metrics

## Run locally

1. Install Python 3.10 or newer.
2. Run `pip install -r requirements.txt`.
3. Run `python train_model.py` to download the configured Pima-style dataset and train the model.
4. Run `python app.py`.
5. Open `http://127.0.0.1:5000` and create an account.

On Windows, you can run `run_project.bat`; it creates a virtual environment, installs dependencies, trains the model if it is missing, and starts the app.

The trained model and SQLite database are generated locally and are excluded from Git. Set a strong `SECRET_KEY` environment variable before any deployment. For production use HTTPS and persistent storage for the database.

## Disclaimer

Predictions are educational estimates only. Consult a qualified healthcare professional for screening, diagnosis, and treatment.
