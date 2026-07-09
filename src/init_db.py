import pandas as pd
from sqlalchemy import create_engine
import json
import os

def init_database():
    print("Inicjalizacja bazy danych SQLite...")
    with open('data/dataset.json', 'r') as file:
        data = json.load(file)
    
    df = pd.DataFrame(data)
    
    # Tworzenie pliku bazy w folderze data
    engine = create_engine('sqlite:///data/jobs_database.db')
    
    # Zapisanie DataFrame do tabeli SQL
    df.to_sql('job_offers', con=engine, if_exists='replace', index=False)
    print("Zakończono. Baza danych gotowa w: data/jobs_database.db")

if __name__ == "__main__":
    init_database()