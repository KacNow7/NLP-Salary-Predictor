import pandas as pd
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import mlflow

def load_data_from_db():
    engine = create_engine('sqlite:///data/jobs_database.db')
    return pd.read_sql('job_offers', con=engine)

def train_model():
    df = load_data_from_db()
    X = df[['title', 'technologies']]
    y = df['salary']

    # Podział danych na treningowe i testowe (80% / 20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    preprocessor = ColumnTransformer(
        transformers=[
            ('title_tfidf', TfidfVectorizer(ngram_range=(1, 2)), 'title'),
            ('tech_tfidf', TfidfVectorizer(token_pattern=r'(?u)\b\w+\b'), 'technologies')
        ]
    )

    n_estimators = 100
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=n_estimators, random_state=42))
    ])

    # Konfiguracja MLflow
    mlflow.set_experiment("Salary_Prediction_Models")
    
    with mlflow.start_run():
        print("Trenowanie modelu...")
        pipeline.fit(X_train, y_train)
        
        # Ewaluacja (Testowanie na danych, których model nie widział)
        predictions = pipeline.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        print(f"Średni błąd przewidywania (MAE): {mae:.2f} PLN")

        # Rejestrowanie parametrów i metryk w MLflow
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_metric("mae", mae)
        mlflow.sklearn.log_model(pipeline, "random_forest_pipeline")

        # Zapis lokalny dla FastAPI
        joblib.dump(pipeline, 'models/salary_predictor.joblib')

if __name__ == "__main__":
    train_model()