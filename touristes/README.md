
# Travel Destination Recommendation System

This is a simple web application that recommends a travel destination based on user preferences.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  **Run the Flask application:**
    ```bash
    python app.py
    ```

2.  **Open your web browser and navigate to:**
    ```
    http://127.0.0.1:5000
    ```

## Project Structure

-   `app.py`: The main Flask application file.
-   `data_preprocessing.py`: Script to preprocess the dataset.
-   `model_training.py`: Script to train the recommendation model.
-   `generate_dataset.py`: Script to generate the synthetic dataset.
-   `tourisme_dataset.csv`: The raw dataset.
-   `processed_data.csv`: The preprocessed dataset.
-   `recommendation_model.joblib`: The trained machine learning model.
-   `preprocessor.joblib`: The saved preprocessing pipeline.
-   `requirements.txt`: A list of the Python packages required to run the application.
-   `templates/index.html`: The HTML template for the user interface.
