import os, sqlite3
from functools import wraps
from pathlib import Path
import joblib, pandas as pd
from flask import Flask, Response, jsonify, redirect, render_template_string, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('DATABASE_PATH', BASE / 'users.db'))
MODEL_PATH = Path(os.environ.get('MODEL_PATH', BASE / 'models' / 'diabetes_model.joblib'))
FEATURES = ['Pregnancies','Glucose','BloodPressure','SkinThickness','Insulin','BMI','DiabetesPedigreeFunction','Age']
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-before-deployment')
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
def connect_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection
with connect_db() as connection:
    connection.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL)')
def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session: return redirect(url_for('login', next=request.path))
        return fn(*args, **kwargs)
    return wrapper
CSS = '''<style>*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:#f4efe6;color:#17211c;font:16px 'Segoe UI',sans-serif;padding:24px}.card{width:min(100%,440px);background:#fffdf8;border:1px solid #ddd;border-radius:20px;padding:32px;box-shadow:0 24px 60px #0a3d3420}.brand{color:#0a3d34;font-size:24px;font-weight:700}.muted{color:#4d5c55}.card label{display:block;font-weight:600;margin-top:16px}.card input{display:block;width:100%;margin-top:6px;padding:12px;border:1px solid #d8d5cb;border-radius:10px;font:inherit;background:#f8f5ef}.pw{display:flex;gap:8px}.pw input{flex:1;min-width:0}.pw button,.submit{border:0;border-radius:10px;padding:11px 14px;cursor:pointer;font:inherit;font-weight:600}.pw button{background:#ebe4d6}.submit{width:100%;margin-top:22px;background:#0f5c4c;color:white}.card a{color:#0f5c4c}.error{color:#a33320;background:#f9e4de;border-radius:8px;padding:10px}</style><script>function togglePw(id,b){let x=document.getElementById(id);x.type=x.type==='password'?'text':'password';b.textContent=x.type==='password'?'Show':'Hide'}</script>'''
LOGIN = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Login | GlycoSight</title>''' + CSS + '''</head><body><main class="card"><div class="brand">● GlycoSight</div><h1>Welcome back</h1><p class="muted">Login to continue.</p>{% if error %}<p class="error">{{ error }}</p>{% endif %}<form method="post"><label>Email</label><input name="email" type="email" autocomplete="email" required><label>Password</label><div class="pw"><input id="password" name="password" type="password" autocomplete="current-password" required><button type="button" onclick="togglePw('password',this)">Show</button></div><button class="submit">Login</button></form><p class="muted">New here? <a href="/signup">Create account</a></p></main></body></html>'''
SIGNUP = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sign up | GlycoSight</title>''' + CSS + '''</head><body><main class="card"><div class="brand">● GlycoSight</div><h1>Create account</h1>{% if error %}<p class="error">{{ error }}</p>{% endif %}<form method="post"><label>Name</label><input name="name" maxlength="100" required><label>Email</label><input name="email" type="email" maxlength="254" required><label>Password (8+ characters)</label><div class="pw"><input id="password" name="password" type="password" minlength="8" required><button type="button" onclick="togglePw('password',this)">Show</button></div><label>Confirm password</label><div class="pw"><input id="confirm" name="confirm_password" type="password" minlength="8" required><button type="button" onclick="togglePw('confirm',this)">Show</button></div><button class="submit">Create account</button></form><p class="muted">Already registered? <a href="/login">Login</a></p></main></body></html>'''
@app.route('/signup', methods=['GET','POST'])
def signup():
    error = None
    if request.method == 'POST':
        name = request.form.get('name','').strip(); email = request.form.get('email','').strip().lower(); password = request.form.get('password','')
        if not name or not email or len(password) < 8: error = 'Fill all fields and use at least 8 characters for password.'
        elif password != request.form.get('confirm_password',''): error = 'Passwords do not match.'
        else:
            try:
                with connect_db() as con: cur = con.execute('INSERT INTO users(name,email,password_hash) VALUES(?,?,?)',(name,email,generate_password_hash(password)))
                session.clear(); session['user_id'] = cur.lastrowid; session['user_name'] = name
                return redirect(url_for('home'))
            except sqlite3.IntegrityError: error = 'This email is already registered.'
    return render_template_string(SIGNUP, error=error)
@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        with connect_db() as con: user = con.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
        if user and check_password_hash(user['password_hash'],request.form.get('password','')):
            session.clear(); session['user_id'] = user['id']; session['user_name'] = user['name']
            target = request.args.get('next','')
            return redirect(target if target.startswith('/') and not target.startswith('//') else url_for('home'))
        error = 'Email or password is incorrect.'
    return render_template_string(LOGIN, error=error)
@app.route('/logout', methods=['GET','POST'])
def logout(): session.clear(); return redirect(url_for('login'))
@app.route('/')
@auth_required
def home():
    html = (BASE / 'index.html').read_text(encoding='utf-8')
    name = str(session.get('user_name','User')).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    bar = '<div style="display:flex;justify-content:flex-end;align-items:center;gap:12px;padding:8px 0;color:#0a3d34"><span>Signed in as '+name+'</span><form method="post" action="/logout"><button class="btn btn-small" type="submit">Logout</button></form></div>'
    return html.replace('</header>',bar+'</header>',1)
@app.route('/<path:filename>')
@auth_required
def assets(filename):
    if not filename.startswith(('css/','js/')): return ('Not found',404)
    path = (BASE / filename).resolve()
    if BASE.resolve() not in path.parents or not path.is_file(): return ('Not found',404)
    content = path.read_text(encoding='utf-8')
    if filename == 'js/app.js':
        content = content.replace('const API_BASE_URL = (window.DIABETES_API_URL || "").replace(/\\/$/, "");','const API_BASE_URL = window.location.origin;')
        content = content.replace('headers: { "Content-Type": "application/json" },','headers: { "Content-Type": "application/json" }, credentials: "same-origin",')
    return Response(content,mimetype='text/css' if filename.endswith('.css') else 'application/javascript')
@app.route('/health')
def health(): return jsonify({'success':True,'status':'ok'})
@app.route('/predict',methods=['POST'])
@auth_required
def predict():
    if not MODEL_PATH.is_file(): return jsonify({'success':False,'error':'Model file missing. Run train_model.py first.'}),503
    try:
        data = request.get_json(force=True)
        if not isinstance(data, dict): return jsonify({'success':False,'error':'Send a JSON object containing all eight features.'}),400
        values = {key:float(data[key]) for key in FEATURES}
        if any(not pd.notna(value) or value < 0 for value in values.values()): return jsonify({'success':False,'error':'Input values must be valid non-negative numbers.'}),400
        for key in ['Glucose','BloodPressure','SkinThickness','Insulin','BMI']:
            if values[key] == 0: values[key] = float('nan')
        artifact = joblib.load(MODEL_PATH); model = artifact.get('model') if isinstance(artifact,dict) else artifact
        probability = float(model.predict_proba(pd.DataFrame([values],columns=FEATURES))[0][1])
        return jsonify({'success':True,'probability':round(probability*100,2),'prediction':int(probability>=0.5),'disclaimer':'Educational estimate only; not a medical diagnosis.'})
    except (KeyError,TypeError,ValueError) as exc: return jsonify({'success':False,'error':'Invalid input: '+str(exc)}),400
    except Exception:
        app.logger.exception('Prediction failed')
        return jsonify({'success':False,'error':'Prediction failed. Check model file and input data.'}),500
if __name__ == '__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT','5000')),debug=False)
