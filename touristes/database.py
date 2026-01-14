import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@db:5432/recommendation_db')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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

