
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from app import app, db, User, Destination, TourismeData

def init_database():
    with app.app_context():
        # Drop all tables if they exist
        db.drop_all()
        # Create all tables
        db.create_all()

        # Load data from CSVs
        destinations_df = pd.read_csv('destinations.csv')
        tourisme_df = pd.read_csv('tourisme_dataset_cleaned.csv')

        # Populate Destinations table
        for _, row in destinations_df.iterrows():
            dest = Destination(
                name=row['Destination'],
                continent=row['Continent'],
                cost_of_living=row['Cout_de_la_Vie'],
                destination_type=row['Type_Destination']
            )
            db.session.add(dest)
        db.session.commit()
        print("Destinations table populated.")

        # Populate TourismeData table
        dest_mapping = {dest.name: dest.id for dest in Destination.query.all()}
        for _, row in tourisme_df.iterrows():
            dest_id = dest_mapping.get(row['Destination'])
            if dest_id:
                data = TourismeData(
                    age=row['Age'],
                    budget=row['Budget'],
                    interest=row['Interet'],
                    duration=row['Duree'],
                    climate=row['Climat'],
                    travel_type=row['Type_Voyage'],
                    season=row['Saison'],
                    nationality=row['Nationalite'],
                    activity=row['Activite'],
                    destination_id=dest_id
                )
                db.session.add(data)
        db.session.commit()
        print("TourismeData table populated.")

        print("Database initialized and populated successfully.")

if __name__ == '__main__':
    init_database()
