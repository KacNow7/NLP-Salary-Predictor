# NLP IT Salary Predictor & Data Pipeline

An End-to-End Machine Learning and Data Engineering project that predicts software engineering salaries based on job titles and required technology stacks. 

Unlike static ML projects relying on flat CSV files, this system features a fully automated Data Pipeline that scrapes live market data, dynamically retrains the NLP model, and serves predictions via a containerized REST API and interactive web UI.

## System Architecture

This project mimics a production-grade MLOps lifecycle, divided into four autonomous micro-components:

1. Data Extraction (Web Scraping): A robust, custom-built Playwright scraper. It bypasses SPA DOM-rendering limitations using native JavaScript injection to reliably extract live job offers and salaries from Polish IT job boards.
2. Data Pipeline & Storage: Raw data is parsed (Regex salary extraction, currency normalization) and appended to a local SQLite database with built-in deduplication.
3. Continuous Training (MLOps): A Python script queries the SQLite DB, cleans the data, vectorizes text using TF-IDF, and trains a RandomForestRegressor. Experiments and metrics are tracked using MLflow.
4. Serving & UI: The trained model is served via FastAPI, which is consumed by an interactive Streamlit frontend. The entire serving layer is containerized using Docker.

## Tech Stack
* Language: Python 3.11+
* Data Engineering: Playwright (with JS injection), Pandas, SQLite, SQLAlchemy, Regex
* Machine Learning: Scikit-learn (TF-IDF, Random Forest), Joblib
* MLOps / Tracking: MLflow
* Backend API: FastAPI, Uvicorn, Pydantic
* Frontend UI: Streamlit
* Infrastructure: Docker, Docker Compose

---

## How to Run the Project

### Phase 1: Data Collection & Model Training (Local Setup)
To populate the database and train the model, you need to run the pipeline locally.

1. Install dependencies:
   pip install -r requirements.txt
   playwright install chromium
   
2. Run the Data Pipeline (Scraper):
   This script will launch a headless browser, bypass cookie banners, extract real-time offers, and populate the jobs_database.db.
   python src/scraper_to_db.py
   
3. Train the ML Model:
   This will query the DB, deduplicate records, train the ML pipeline, and save the artifact to /models.
   python src/train.py
   
   (Optional) To view the training metrics and experiments, run mlflow ui and open localhost:5000.

### Phase 2: Launching the Application (Dockerized)
Once the database is populated and the model is generated, you can spin up the serving layer using Docker.

docker-compose up --build

This command spins up a virtual network with two containers:
* Frontend (Streamlit): Available at http://localhost:8501
* Backend API (FastAPI): Available at http://localhost:8000

---

## API Documentation
When the Docker containers are running, you can access the auto-generated Swagger UI documentation at http://localhost:8000/docs.

Example Inference Request (POST /predict):

{
  "title": "Mid Python Developer",
  "technologies": "python django postgresql docker aws"
}

## Disclaimer
This project was built strictly for educational and portfolio purposes. The web scraping scripts are designed to have a minimal footprint and respect target server loads. No personal data is collected or stored.