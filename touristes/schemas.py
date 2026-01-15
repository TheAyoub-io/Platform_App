from pydantic import BaseModel
from typing import List
from datetime import date

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class User(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class RecommendationRequest(BaseModel):
    Age: int
    Budget: int
    Interet: str
    Duree: int
    Climat: str
    Continent: str
    Type_Destination: str

# Schemas for Hotel, Room, and Booking
class RoomBase(BaseModel):
    room_type: str
    price: float
    availability: int

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: int
    hotel_id: int

    class Config:
        orm_mode = True

class HotelBase(BaseModel):
    name: str
    destination: str
    rating: int

class HotelCreate(HotelBase):
    pass

class Hotel(HotelBase):
    id: int
    rooms: List[Room] = []

    class Config:
        orm_mode = True

class BookingBase(BaseModel):
    room_id: int
    start_date: date
    end_date: date

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
