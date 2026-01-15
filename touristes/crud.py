from sqlalchemy.orm import Session
import schemas
import database
from security import get_password_hash

# User CRUD
def get_user_by_username(db: Session, username: str):
    return db.query(database.User).filter(database.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = database.User(username=user.username, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Hotel and Booking CRUD
def get_hotels_by_destination(db: Session, destination: str):
    return db.query(database.Hotel).filter(database.Hotel.destination.ilike(f"%{destination}%")).all()

def create_hotel(db: Session, hotel: schemas.HotelCreate):
    db_hotel = database.Hotel(**hotel.dict())
    db.add(db_hotel)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel

def get_room(db: Session, room_id: int):
    # Lock the row for update to prevent race conditions
    return db.query(database.Room).filter(database.Room.id == room_id).with_for_update().first()

def create_booking(db: Session, user_id: int, booking: schemas.BookingCreate):
    # The transaction begins with the first query.
    # The `get_room` function now locks the selected room row.
    db_room = get_room(db, room_id=booking.room_id)

    if not db_room:
        db.rollback() # Release the lock
        return None, "Room not found."

    if db_room.availability <= 0:
        db.rollback() # Release the lock
        return None, "No rooms available."

    # The row is locked, so this operation is safe.
    db_room.availability -= 1

    db_booking = database.Booking(
        user_id=user_id,
        room_id=booking.room_id,
        start_date=booking.start_date,
        end_date=booking.end_date
    )
    db.add(db_booking)

    # Committing the session persists all changes (availability and new booking)
    # and releases the lock.
    db.commit()
    db.refresh(db_booking)

    return db_booking, None
