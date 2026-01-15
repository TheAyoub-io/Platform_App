from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, JSONResponse
from jose import jwt, JWTError
import pandas as pd
import joblib
from sqlalchemy.orm import Session
from pathlib import Path
import requests
import os

import crud, database, schemas, security
from database import SessionLocal, engine

database.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Load models
model = joblib.load('recommendation_model.joblib')
preprocessor = joblib.load('preprocessor.joblib')
label_encoder = joblib.load('label_encoder.joblib')

templates = Jinja2Templates(directory="templates")

# In-memory database for hotels
hotels_db = [
    {"name": "Grand Hyatt", "rating": 5},
    {"name": "The Ritz-Carlton", "rating": 5},
    {"name": "Holiday Inn", "rating": 4},
    {"name": "Marriott", "rating": 4},
]


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
def recommend(rec_request: schemas.RecommendationRequest, current_user: database.User = Depends(get_current_user)):
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
        
        return templates.TemplateResponse("recommendation_result.html", {"request": {}, "recommendation": prediction[0]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/hotels")
def hotels(request: Request):
    return templates.TemplateResponse("hotels.html", {"request": request, "hotels": hotels_db})

@app.get("/currency")
def currency(request: Request):
    return templates.TemplateResponse("currency_converter.html", {"request": request})

@app.get("/taxis")
def taxis(request: Request):
    return templates.TemplateResponse("taxis.html", {"request": request})

@app.post("/taxis")
async def book_taxi(request: Request):
    return JSONResponse(content={"message": "Driver found! Your ride is on the way."})

@app.get("/locales/{lng}.json")
async def read_locale(lng: str):
    file_path = f"locales/{lng}.json"
    if not Path(file_path).is_file():
        raise HTTPException(status_code=404, detail="Locale not found")
    return FileResponse(file_path)

@app.get("/api/currency/rates")
async def get_currency_rates():
    api_key = os.environ.get("EXCHANGE_RATE_API_KEY", "YOUR_API_KEY")
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return JSONResponse(content=response.json())
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/currency/convert")
async def convert_currency(amount: float, from_currency: str, to_currency: str):
    api_key = os.environ.get("EXCHANGE_RATE_API_KEY", "YOUR_API_KEY")
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}/{amount}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return JSONResponse(content=response.json())
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
