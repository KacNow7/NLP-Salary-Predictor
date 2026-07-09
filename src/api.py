from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

# Inicjalizacja aplikacji i załadowanie modelu do pamięci
app = FastAPI(title="NLP Salary Predictor API", version="1.0")
MODEL_PATH = "models/salary_predictor.joblib"

try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    model = None

# Walidacja danych wejściowych
class JobRequest(BaseModel):
    title: str
    technologies: str

@app.post("/predict")
def predict_salary(request: JobRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Model nie zostal zaladowany. Uruchom najpierw train.py.")
    
    # Konwersja danych z API do formatu Pandas DataFrame
    input_data = pd.DataFrame([{
        "title": request.title,
        "technologies": request.technologies
    }])
    
    # Wykonanie predykcji
    prediction = model.predict(input_data)
    
    return {
        "title": request.title,
        "predicted_salary_pln": round(prediction[0], 2)
    }