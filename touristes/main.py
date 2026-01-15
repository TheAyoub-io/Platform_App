from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from jose import jwt, JWTError
import pandas as pd
import joblib
from sqlalchemy.orm import Session
from pathlib import Path

import crud, database, schemas, security
from database import SessionLocal, engine
from .routers import hotels, taxis, currency

# Create all tables
database.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include routers
app.include_router(hotels.router)
app.include_router(taxis.router)
app.include_router(currency.router)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Load models
model = joblib.load('recommendation_model.joblib')
preprocessor = joblib.load('preprocessor.joblib')
label_encoder = joblib.load('label_encoder.joblib')

templates = Jinja2Templates(directory="templates")

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
        
        return templates.TemplateResponse("_recommendation_result.html", {"request": request, "recommendation": prediction[0]})
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

# Locale endpoint
@app.get("/locales/{lng}.json")
async def read_locale(lng: str):
    file_path = f"locales/{lng}.json"
    if not Path(file_path).is_file():
        raise HTTPException(status_code=404, detail="Locale not found")
    return FileResponse(file_path)
