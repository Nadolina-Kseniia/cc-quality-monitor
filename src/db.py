import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    url = os.getenv("DB_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/cc_quality")
    return create_engine(url)

def load_data(engine):
    return (
        pd.read_sql("SELECT * FROM operators", engine),
        pd.read_sql("SELECT * FROM calls", engine),
    )