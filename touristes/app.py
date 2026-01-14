
import os
from flask import Flask, render_template, request, redirect, url_for, flash
import joblib
import pandas as pd
import logging
from transformers import FeatureCreator
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@db:5432/recommendation_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    continent = db.Column(db.String(50))
    cost_of_living = db.Column(db.Float)
    destination_type = db.Column(db.String(50))
    tourism_data = db.relationship('TourismeData', backref='destination', lazy=True)

    def __repr__(self):
        return f'<Destination {self.name}>'

class TourismeData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    budget = db.Column(db.Float)
    interest = db.Column(db.String(50))
    duration = db.Column(db.Integer)
    climate = db.Column(db.String(50))
    travel_type = db.Column(db.String(50))
    season = db.Column(db.String(50))
    nationality = db.Column(db.String(50))
    activity = db.Column(db.String(50))
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)

    def __repr__(self):
        return f'<TourismeData {self.id}>'


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    handlers=[logging.FileHandler("flask_app.log"),
                              logging.StreamHandler()])

# Load the trained model, preprocessor, and label encoder
try:
    model = joblib.load('recommendation_model.joblib')
    preprocessor = joblib.load('preprocessor.joblib')
    label_encoder = joblib.load('label_encoder.joblib')
    app.logger.info("Model, preprocessor, and label encoder loaded successfully.")
except FileNotFoundError as e:
    app.logger.error(f"Error loading model files: {e}")
    model = None
    preprocessor = None
    label_encoder = None

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
            if user_exists:
                flash('Username or email already exists.')
                return redirect(url_for('signup'))

            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        except Exception as e:
            app.logger.error(f"An error occurred during signup: {e}", exc_info=True)
            flash('An unexpected error occurred. Please try again.')
            return redirect(url_for('signup'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/')
def home():
    """Renders the home page."""
    interests = ['Culture', 'Ville', 'Plage', 'Aventure', 'Nature', 'Gastronomie', 'Shopping', 'Histoire']
    climates = ['Tempéré', 'Chaud', 'Froid', 'Désertique']
    travel_types = ['Solo', 'Couple', 'Famille', 'Amis']
    seasons = ['Printemps', 'Été', 'Automne', 'Hiver']
    nationalities = ['Français', 'Américain', 'Chinois', 'Allemand', 'Japonais', 'Britannique', 'Indien', 'Brésilien', 'Canadien', 'Australien']
    activities = ['Musée', 'Gastronomie', 'Shopping', 'Surf', 'Histoire', 'Carnaval', 'Opéra', 'Architecture', 'Aurores boréales', 'Ski', 'Randonnée', 'Photographie', 'Tango', 'Romance', 'Musique']
    return render_template('index.html', interests=interests, climates=climates, travel_types=travel_types, seasons=seasons, nationalities=nationalities, activities=activities)

@app.route('/recommend', methods=['POST'])
@login_required
def recommend():
    """Handles the recommendation request."""
    if not all([model, preprocessor, label_encoder]):
        return render_template('index.html', error="Model is not available. Please check server logs.")

    try:
        features = {
            'Age': [int(request.form['Age'])],
            'Budget': [int(request.form['Budget'])],
            'Interet': [request.form['Interet']],
            'Duree': [int(request.form['Duree'])],
            'Climat': [request.form['Climat']],
            'Type_Voyage': [request.form['Type_Voyage']],
            'Saison': [request.form['Saison']],
            'Nationalite': [request.form['Nationalite']],
            'Activite': [request.form['Activite']]
        }
        input_df = pd.DataFrame(features)
        app.logger.info(f"Received user input: {features}")

        input_processed = preprocessor.transform(input_df)
        prediction_encoded = model.predict(input_processed)
        prediction = label_encoder.inverse_transform(prediction_encoded)

        app.logger.info(f"Prediction successful. Recommended destination: {prediction[0]}")
        return render_template('index.html', recommendation=prediction[0])

    except Exception as e:
        app.logger.error(f"An error occurred during recommendation: {e}", exc_info=True)
        return render_template('index.html', error="An error occurred while getting your recommendation.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
