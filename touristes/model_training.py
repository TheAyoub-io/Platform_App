
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.metrics import accuracy_score, classification_report
import joblib
import numpy as np


# --- Main Script ---

# Load and prepare data from CSV files
df_tourisme = pd.read_csv('tourisme_dataset_cleaned.csv')
df_destinations = pd.read_csv('destinations.csv')
=======
from transformers import FeatureCreator

import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# --- Main Script ---

# Load and prepare data from PostgreSQL
db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:Kxsd2882@localhost:5432/recommendation_db')
engine = create_engine(db_url)

query_tourisme = "SELECT * FROM tourisme_data;"
query_destinations = "SELECT * FROM destination;"

df_tourisme = pd.read_sql(query_tourisme, engine)
df_destinations = pd.read_sql(query_destinations, engine)

# Rename columns to match original CSVs for merging
df_destinations.rename(columns={'name': 'Destination', 'cost_of_living': 'Cout_de_la_Vie', 'destination_type': 'Type_Destination'}, inplace=True)
df_tourisme.rename(columns={'interest': 'Interet', 'duration': 'Duree', 'climate': 'Climat'}, inplace=True)

# Map destination_id to destination name
dest_id_to_name = df_destinations.set_index('id')['Destination'].to_dict()
df_tourisme['Destination'] = df_tourisme['destination_id'].map(dest_id_to_name)


# Merge dataframes
df = pd.merge(df_tourisme, df_destinations, on='Destination')
df.drop_duplicates(inplace=True)

# Separate features (X) and target (y)
X = df.drop('Destination', axis=1)
y = df['Destination']

# Encode the target variable before splitting
le = LabelEncoder()
y_encoded = le.fit_transform(y)
joblib.dump(le, 'label_encoder.joblib')

# Split data into training and testing sets to prevent data leakage
X_train, X_test, y_train_encoded, y_test_encoded = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Define column types for preprocessing

categorical_features = ['Interet', 'Climat', 'Type_Voyage', 'Saison', 'Nationalite', 'Activite']
numerical_features = ['Age', 'Budget', 'Duree']

categorical_features = ['Interet', 'Climat', 'continent', 'Type_Destination', 'Interet_Continent']
numerical_features = ['age', 'budget', 'Duree', 'Budget_per_day', 'Cout_de_la_Vie', 'Budget_Ajuste']


# Create preprocessing pipelines for numerical and categorical features
numerical_transformer = StandardScaler()
categorical_transformer = OneHotEncoder(handle_unknown='ignore')

# Create a preprocessor to apply different transformations to different columns
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_transformer, numerical_features),
        ('cat', categorical_transformer, categorical_features)
    ],
    remainder='drop' # Drop original columns that are not needed
)

# Create the full feature engineering and preprocessing pipeline
full_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor)
])

# Fit the entire pipeline on the training data and save it
full_pipeline.fit(X_train)
joblib.dump(full_pipeline, 'preprocessor.joblib')

# Transform training and testing data
X_train_processed = full_pipeline.transform(X_train)
X_test_processed = full_pipeline.transform(X_test)

# Train the K-Nearest Neighbors model
model = KNN(n_neighbors=5)
model.fit(X_train_processed, y_train_encoded)
joblib.dump(model, 'recommendation_model.joblib')

# Evaluate the model
y_pred_encoded = model.predict(X_test_processed)
accuracy = accuracy_score(y_test_encoded, y_pred_encoded)
report = classification_report(y_test_encoded, y_pred_encoded, target_names=le.classes_)

# Save performance report
with open('model_performance.txt', 'w') as f:
    f.write(f"Accuracy: {accuracy:.4f}\n\n")
    f.write("Classification Report:\n")
    f.write(report)

print("--- Model Performance ---")
print(report)
print("Model training, preprocessing pipeline, and label encoder have been saved.")
