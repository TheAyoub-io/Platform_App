from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Correctly import from the top-level modules
from .. import crud, schemas, database
from ..main import get_db, get_current_user

router = APIRouter(
    prefix="/api/hotels",
    tags=["hotels"],
)

@router.get("/search", response_model=List[schemas.Hotel])
async def search_hotels(destination: str, db: Session = Depends(get_db)):
    hotels = crud.get_hotels_by_destination(db, destination=destination)
    return hotels

@router.post("/book", response_model=schemas.Booking)
async def book_hotel(booking: schemas.BookingCreate, db: Session = Depends(get_db), current_user: database.User = Depends(get_current_user)):
    if booking.end_date <= booking.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date.")

    db_booking, error_msg = crud.create_booking(db=db, user_id=current_user.id, booking=booking)
    if error_msg:
        raise HTTPException(status_code=400, detail=error_msg)
    return db_booking
