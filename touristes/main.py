from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
import pandas as pd
import joblib
from sqlalchemy.orm import Session

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

# Dependency to get the DB session
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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
        
        return templates.TemplateResponse("index.html", {"request": request, "recommendation": prediction[0]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home(request: Request):
    continents = ['Europe', 'Amerique du Nord', 'Asie', 'Oceanie', 'Afrique', 'Amerique du Sud']
    destination_types = ['Megalopole', 'Historique', 'Ile']
    return templates.TemplateResponse("index.html", {"request": request, "continents": continents, "destination_types": destination_types})

    
