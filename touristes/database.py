import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL set for the connection")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    bookings = relationship("Booking", back_populates="user")

class Hotel(Base):
    __tablename__ = "hotels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    destination = Column(String, index=True, nullable=False)
    rating = Column(Integer, nullable=False)
    rooms = relationship("Room", back_populates="hotel")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    room_type = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    availability = Column(Integer, nullable=False)
    hotel = relationship("Hotel", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")

class Destination(Base):
    __tablename__ = "destination"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    continent = Column(String)
    cost_of_living = Column(Float)
    destination_type = Column(String)
    tourism_data = relationship('TourismeData', backref='destination', lazy=True)

class TourismeData(Base):
    __tablename__ = "tourisme_data"
    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    budget = Column(Float)
    interest = Column(String)
    duration = Column(Integer)
    climate = Column(String)
    destination_id = Column(Integer, ForeignKey('destination.id'), nullable=False)
