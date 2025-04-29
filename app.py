import os
from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import joblib
from ultralytics import YOLO
from scipy.io import loadmat

# --- App setup ---
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-me')

# --- Upload configuration ---
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Database & Login ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# --- Load ML models ---
# YOLO crack detector
yolo_path = os.path.join(app.root_path, 'models', r'C:\Users\2004s\OneDrive\Desktop\full project 4\Full project 3\best.onnx')
detector = YOLO(yolo_path, task='detect')
# Numeric-feature predictor
feature_model = joblib.load(os.path.join(app.root_path, 'models', r'C:\Users\2004s\OneDrive\Desktop\full project 4\Full project 3\models\best_model.pkl'))
scaler = joblib.load(os.path.join(app.root_path, 'models', r'C:\Users\2004s\OneDrive\Desktop\full project 4\Full project 3\models\scaler.pkl'))
# .mat machinery fault detector
machinery_model = joblib.load(os.path.join(app.root_path, 'model', r'C:\Users\2004s\OneDrive\Desktop\full project 4\Full project 3\machinery_model.pkl'))

def extract_features(signal: np.ndarray) -> np.ndarray:
    return np.array([
        np.mean(signal),
        np.std(signal),
        np.max(signal),
        np.min(signal),
        np.median(signal),
        np.sum(np.square(signal))
    ])

# --- Routes ---
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Both fields required', 'warning')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('register'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid credentials.', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You’ve been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(filepath)
    img = Image.open(filepath)
    bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    results = detector.predict(source=bgr, conf=0.25, iou=0.45)
    annotated = results[0].plot()
    out_img = Image.fromarray(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
    buf = BytesIO()
    out_img.save(buf, format='JPEG')
    buf.seek(0)
    os.remove(filepath)
    return send_file(buf, mimetype='image/jpeg')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    features = data.get('features')
    if features is None:
        return jsonify({'error': 'No features provided'}), 400
    try:
        arr = np.array(features).reshape(1, -1)
        scaled = scaler.transform(arr)
        pred = feature_model.predict(scaled)[0]
        return jsonify({'prediction': int(pred)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/fault_detect', methods=['POST'])
@login_required
def fault_detect():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if not file.filename.endswith('.mat'):
        return jsonify({'error': 'Invalid file type'}), 400
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(filepath)
    try:
        mat = loadmat(filepath)
        if 'H' not in mat:
            raise KeyError('Variable "H" not found')
        signal = np.ravel(mat['H'])
        feats = extract_features(signal).reshape(1, -1)
        pr = machinery_model.predict(feats)[0]
        label = 'Normal' if pr == 0 else 'Faulty'
        return jsonify({'result': label})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        os.remove(filepath)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)