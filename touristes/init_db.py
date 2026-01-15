import pandas as pd
from database import Base, engine, SessionLocal
from database import Hotel, Room, Destination, TourismeData

def init_db():
    # Drop and recreate all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # --- Populate Recommendation Data from CSVs ---
        try:
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
                db.add(dest)
            db.commit()
            print("Destinations table populated.")

            # Populate TourismeData table
            dest_mapping = {dest.name: dest.id for dest in db.query(Destination).all()}
            for _, row in tourisme_df.iterrows():
                dest_id = dest_mapping.get(row['Destination'])
                if dest_id:
                    data = TourismeData(
                        age=row['Age'],
                        budget=row['Budget'],
                        interest=row['Interet'],
                        duration=row['Duree'],
                        climate=row['Climat'],
                        destination_id=dest_id
                    )
                    db.add(data)
            db.commit()
            print("TourismeData table populated.")
        except FileNotFoundError as e:
            print(f"Skipping recommendation data population: {e}")


        # --- Populate Hotel Test Data ---
        hotel1 = Hotel(name="Grand Hyatt", destination="Paris", rating=5)
        hotel2 = Hotel(name="The Ritz-Carlton", destination="Paris", rating=5)
        hotel3 = Hotel(name="Holiday Inn", destination="New York", rating=4)
        hotel4 = Hotel(name="Marriott", destination="New York", rating=4)
        hotel5 = Hotel(name="Hotel Shibuya", destination="Tokyo", rating=4)

        db.add_all([hotel1, hotel2, hotel3, hotel4, hotel5])
        db.commit()

        # Create Rooms for each hotel
        room1_1 = Room(hotel_id=hotel1.id, room_type="Standard", price=250.0, availability=10)
        room1_2 = Room(hotel_id=hotel1.id, room_type="Suite", price=500.0, availability=5)

        room2_1 = Room(hotel_id=hotel2.id, room_type="Deluxe", price=800.0, availability=3)

        room3_1 = Room(hotel_id=hotel3.id, room_type="Standard", price=150.0, availability=20)
        room3_2 = Room(hotel_id=hotel3.id, room_type="Queen", price=200.0, availability=15)

        room4_1 = Room(hotel_id=hotel4.id, room_type="King", price=220.0, availability=18)

        room5_1 = Room(hotel_id=hotel5.id, room_type="Capsule", price=80.0, availability=30)
        room5_2 = Room(hotel_id=hotel5.id, room_type="Double", price=120.0, availability=12)

        db.add_all([room1_1, room1_2, room2_1, room3_1, room3_2, room4_1, room5_1, room5_2])
        db.commit()
        print("Hotel test data populated.")

        print("Database initialized and populated successfully.")

    finally:
        db.close()

if __name__ == "__main__":
    init_db()
