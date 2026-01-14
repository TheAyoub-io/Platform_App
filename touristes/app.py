
import os
from flask import Flask, render_template, request, redirect, url_for, flash
import joblib
import pandas as pd
import logging
from transformers import FeatureCreator
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')

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
