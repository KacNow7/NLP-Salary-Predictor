# NLP Salary Predictor (MLOps)

This repository contains an End-to-End Machine Learning project that leverages Natural Language Processing (NLP) to predict software engineering salaries based on job titles and required technology stacks.

## Architecture & Tech Stack
* **Language:** Python 3.11+
* **Data Processing & ML:** Pandas, Scikit-learn (RandomForest, TF-IDF)
* **Model Serialization:** Joblib
* **API / Serving:** FastAPI, Uvicorn, Pydantic

## Project Structure
* `/data` - Contains the raw and processed JSON datasets (collected via external scrapers).
* `/models` - Directory for serialized `.joblib` model artifacts.
* `/src/train.py` - ML Pipeline script responsible for text vectorization (TF-IDF) and model training.
* `/src/api.py` - FastAPI application for real-time model inference.

## Usage

### 1. Model Training
Run the training script to generate the model artifact based on the current dataset.
```bash
python src/train.py