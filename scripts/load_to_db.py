import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/cc_quality")
engine = create_engine(DB_URL)
root = Path(__file__).resolve().parent.parent

ops = pd.read_csv(root / "data" / "operators.csv", parse_dates=["hire_date"])
calls = pd.read_csv(root / "data" / "calls.csv", parse_dates=["start_time"])

ops.to_sql("operators", engine, if_exists="append", index=False)
calls.to_sql("calls", engine, if_exists="append", index=False)
print(f"✔ Loaded {len(ops)} operators, {len(calls)} calls")