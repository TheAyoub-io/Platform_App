import pandas as pd
import numpy as np

def clean_dataset(input_path='tourisme_dataset.csv', output_path='tourisme_dataset_cleaned.csv'):
    """
    Loads the dataset, cleans it, and saves the cleaned version.
    """
    # Load the dataset
    df = pd.read_csv(input_path)
    print(f"Initial dataset shape: {df.shape}")

    # 1. Handle duplicates
    df.drop_duplicates(inplace=True)
    print(f"Shape after dropping duplicates: {df.shape}")

    # 2. Correct inconsistencies (typos)
    df['Interet'] = df['Interet'].replace('Cultuer', 'Culture')
    print("Corrected 'Cultuer' to 'Culture' in 'Interet' column.")

    # 3. Handle missing values
    # For 'Budget', we'll fill NaN with the median of the column
    if df['Budget'].isnull().any():
        median_budget = df['Budget'].median()
        df['Budget'].fillna(median_budget, inplace=True)
        print(f"Filled NaN values in 'Budget' with median value: {median_budget:.2f}")

    # Verify that there are no more missing values in 'Budget'
    if not df['Budget'].isnull().any():
        print("No more missing values in 'Budget' column.")

    # Save the cleaned dataset
    df.to_csv(output_path, index=False)
    print(f"Cleaned dataset saved to '{output_path}'. Final shape: {df.shape}")

if __name__ == '__main__':
    clean_dataset()
