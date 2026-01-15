from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from jose import jwt, JWTError
import pandas as pd
import joblib
from sqlalchemy.orm import Session
from pathlib import Path
import requests
import os
from cachetools import TTLCache

import crud, database, schemas, security
from database import SessionLocal, engine

database.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Cache for currency rates (TTL: 1 hour)
currency_cache = TTLCache(maxsize=10, ttl=3600)

# Load models
model = joblib.load('recommendation_model.joblib')
preprocessor = joblib.load('preprocessor.joblib')
label_encoder = joblib.load('label_encoder.joblib')

templates = Jinja2Templates(directory="templates")

# In-memory database for hotels
hotels_db = [
    {"id": 1, "name": "Grand Hyatt", "rating": 5, "destination": "Paris", "availability": 10},
    {"id": 2, "name": "The Ritz-Carlton", "rating": 5, "destination": "Paris", "availability": 5},
    {"id": 3, "name": "Holiday Inn", "rating": 4, "destination": "New York", "availability": 20},
    {"id": 4, "name": "Marriott", "rating": 4, "destination": "New York", "availability": 15},
    {"id": 5, "name": "Hotel Shibuya", "rating": 4, "destination": "Tokyo", "availability": 8},
]


# Pydantic models for request bodies
class HotelBookingRequest(BaseModel):
    hotel_id: int

class TaxiBookingRequest(BaseModel):
    pickup: str
    destination: str
    fare: float


# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/signup/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/recommend/")
def recommend(request: Request, rec_request: schemas.RecommendationRequest, current_user: database.User = Depends(get_current_user)):
    try:
        features = {
            'Age': [rec_request.Age],
            'Budget': [rec_request.Budget],
            'Interet': [rec_request.Interet],
            'Duree': [rec_request.Duree],
            'Climat': [rec_request.Climat],
            'Continent': [rec_request.Continent],
            'Cout_de_la_Vie': [3.3], # Placeholder value
            'Type_Destination': [rec_request.Type_Destination]
        }
        input_df = pd.DataFrame(features)
        input_processed = preprocessor.transform(input_df)
        prediction_encoded = model.predict(input_processed)
        prediction = label_encoder.inverse_transform(prediction_encoded)
        
        return templates.TemplateResponse("recommendation_result.html", {"request": request, "recommendation": prediction[0]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Page serving endpoints
@app.get("/")
def home(request: Request):
    continents = ['Europe', 'Amerique du Nord', 'Asie', 'Oceanie', 'Afrique', 'Amerique du Sud']
    destination_types = ['Megalopole', 'Historique', 'Ile']
    return templates.TemplateResponse("index.html", {"request": request, "continents": continents, "destination_types": destination_types})

@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/hotels")
def hotels_page(request: Request):
    return templates.TemplateResponse("hotels.html", {"request": request})

@app.get("/currency")
def currency_page(request: Request):
    return templates.TemplateResponse("currency_converter.html", {"request": request})

@app.get("/taxis")
def taxis_page(request: Request):
    return templates.TemplateResponse("taxis.html", {"request": request})


# API Endpoints for services

# Hotel API
@app.get("/api/hotels/search")
async def search_hotels(destination: str):
    results = [hotel for hotel in hotels_db if hotel["destination"].lower() == destination.lower()]
    return JSONResponse(content=results)

@app.post("/api/hotels/book")
async def book_hotel(booking: HotelBookingRequest):
    hotel_id = booking.hotel_id
    hotel = next((h for h in hotels_db if h["id"] == hotel_id), None)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    if hotel["availability"] <= 0:
        raise HTTPException(status_code=400, detail="No rooms available")

    hotel["availability"] -= 1
    return JSONResponse(content={"message": f"Successfully booked a room at {hotel['name']}. Remaining rooms: {hotel['availability']}"})

# Taxi API
@app.post("/api/taxis/book")
async def book_taxi(booking: TaxiBookingRequest):
    return JSONResponse(content={"message": f"Driver found for your ride from {booking.pickup} to {booking.destination}! Your ride is on the way."})

# Locale endpoint
@app.get("/locales/{lng}.json")
async def read_locale(lng: str):
    file_path = f"locales/{lng}.json"
    if not Path(file_path).is_file():
        raise HTTPException(status_code=404, detail="Locale not found")
    return FileResponse(file_path)

# Currency Converter API Proxy
@app.get("/api/currency/rates")
async def get_currency_rates():
    cache_key = "currency_rates_USD"
    if cache_key in currency_cache:
        return JSONResponse(content=currency_cache[cache_key])

    api_key = os.environ.get("EXCHANGE_RATE_API_KEY", "YOUR_API_KEY")
    if api_key == "YOUR_API_KEY":
        raise HTTPException(status_code=500, detail="API key for currency conversion is not configured.")

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("result") == "success":
            currency_cache[cache_key] = data
            return JSONResponse(content=data)
        else:
            raise HTTPException(status_code=502, detail="Failed to fetch valid data from currency API.")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Error communicating with currency API: {e}")

@app.get("/api/currency/convert")
async def convert_currency(amount: float, from_currency: str, to_currency: str):
    cache_key = "currency_rates_USD"

    if cache_key not in currency_cache:
        await get_currency_rates()

    rates_data = currency_cache.get(cache_key)
    if not rates_data or "conversion_rates" not in rates_data:
        raise HTTPException(status_code=500, detail="Currency rates are not available in cache.")

    rates = rates_data["conversion_rates"]

    if from_currency not in rates or to_currency not in rates:
        raise HTTPException(status_code=404, detail=f"Currency code not found. Cannot convert from {from_currency} to {to_currency}.")

    amount_in_usd = amount / rates[from_currency]
    converted_amount = amount_in_usd * rates[to_currency]

    return JSONResponse(content={
        "result": "success",
        "from": from_currency,
        "to": to_currency,
        "amount": amount,
        "conversion_result": converted_amount
    })
