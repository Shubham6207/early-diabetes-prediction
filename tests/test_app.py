import sqlite3
import joblib
import app as webapp

def setup_database(path):
    with sqlite3.connect(path) as connection:
        connection.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL)')

def test_health_endpoint():
    client = webapp.app.test_client()
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'

def test_signup_login_home_and_logout(tmp_path, monkeypatch):
    database = tmp_path / 'users.db'
    setup_database(database)
    monkeypatch.setattr(webapp, 'DB_PATH', database)
    monkeypatch.setattr(webapp, 'MODEL_PATH', tmp_path / 'missing-model.joblib')
    client = webapp.app.test_client()
    assert client.get('/').status_code == 302
    response = client.post('/signup', data={'name':'Test User','user_id':'testuser123','password':'SecurePass123','confirm_password':'SecurePass123'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'GlycoSight' in response.data
    with sqlite3.connect(database) as connection:
        saved = connection.execute('SELECT password_hash, user_id FROM users WHERE user_id=?', ('testuser123',)).fetchone()
    assert saved is not None
    assert saved[0] != 'SecurePass123'
    assert saved[1] == 'testuser123'
    client.post('/logout')
    failed = client.post('/login', data={'user_id':'testuser123','password':'wrong-password'})
    assert b'User ID or password is incorrect.' in failed.data
    response = client.post('/login', data={'user_id':'testuser123','password':'SecurePass123'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'GlycoSight' in response.data
    assert b'Logout' in response.data
    response = client.post('/predict', json={'Pregnancies':1,'Glucose':118,'BloodPressure':72,'SkinThickness':23,'Insulin':79,'BMI':28.4,'DiabetesPedigreeFunction':0.372,'Age':33})
    assert response.status_code == 503
    client.post('/logout')
    assert client.get('/').status_code == 302

def test_signup_password_mismatch(tmp_path, monkeypatch):
    database = tmp_path / 'users.db'
    setup_database(database)
    monkeypatch.setattr(webapp, 'DB_PATH', database)
    client = webapp.app.test_client()
    response = client.post('/signup', data={'name':'Test User','user_id':'testuser123','password':'SecurePass123','confirm_password':'DifferentPass123'})
    assert response.status_code == 200
    assert b'Passwords do not match.' in response.data

class DummyModel:
    def predict_proba(self, frame):
        assert len(frame) == 1
        return [[0.75, 0.25]]

def test_prediction_endpoint_with_model(tmp_path, monkeypatch):
    database = tmp_path / 'users.db'
    setup_database(database)
    model_path = tmp_path / 'model.joblib'
    joblib.dump({'model': DummyModel(), 'features': webapp.FEATURES}, model_path)
    monkeypatch.setattr(webapp, 'DB_PATH', database)
    monkeypatch.setattr(webapp, 'MODEL_PATH', model_path)
    client = webapp.app.test_client()
    client.post('/signup', data={'name':'Test User','user_id':'testuser123','password':'SecurePass123','confirm_password':'SecurePass123'})
    response = client.post('/predict', json={'Pregnancies':1,'Glucose':0,'BloodPressure':72,'SkinThickness':23,'Insulin':79,'BMI':28.4,'DiabetesPedigreeFunction':0.372,'Age':33})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert payload['probability'] == 25.0
    assert payload['prediction'] == 0
