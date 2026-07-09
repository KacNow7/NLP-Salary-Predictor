import pandas as pd
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import joblib

def load_data(filepath: str) -> pd.DataFrame:
    print(f"Wczytywanie danych z {filepath}...")
    with open(filepath, 'r') as file:
        data = json.load(file)
    return pd.DataFrame(data)

def train_model():
    df = load_data('data/dataset.json')
    
    X = df[['title', 'technologies']]
    y = df['salary']

    print("Budowa potoku (Pipeline) NLP...")
    # ColumnTransformer -osobna analiza tytułu i technologii
    preprocessor = ColumnTransformer(
        transformers=[
            ('title_tfidf', TfidfVectorizer(ngram_range=(1, 2)), 'title'),
            ('tech_tfidf', TfidfVectorizer(token_pattern=r'(?u)\b\w+\b'), 'technologies')
        ]
    )

    # Random Forest
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    print("Trenowanie modelu (Model fit)...")
    pipeline.fit(X, y)

    model_path = 'models/salary_predictor.joblib'
    joblib.dump(pipeline, model_path)
    print(f"Sukces! Model zapisany w: {model_path}")

if __name__ == "__main__":
    train_model()