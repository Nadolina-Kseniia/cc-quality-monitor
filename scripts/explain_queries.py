import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pathlib import Path
from sqlalchemy import text
from dotenv import load_dotenv
from src.db import get_engine  # Импортируем наш движок

load_dotenv()


def save_explain(engine, query: str, filepath: str):
    with engine.connect() as conn:
        result = conn.execute(text(f"EXPLAIN ANALYZE {query}"))
        plan = "\n".join(row[0] for row in result)
        Path(filepath).write_text(plan, encoding="utf-8")
        print(f"✔ Saved to {filepath}")


def main():
    engine = get_engine()
    query = "SELECT operator_id, COUNT(*) FROM calls WHERE start_time >= '2026-10-15' GROUP BY operator_id;"

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)

    # 1. Симулируем "ДО" (удаляем индекс)
    with engine.connect() as conn:
        conn.execute(text("DROP INDEX IF EXISTS idx_calls_start;"))
        conn.commit()
    save_explain(engine, query, out_dir / "explain_before.txt")

    # 2. Симулируем "ПОСЛЕ" (создаем индекс)
    with engine.connect() as conn:
        conn.execute(text("CREATE INDEX idx_calls_start ON calls(start_time);"))
        conn.commit()
    save_explain(engine, query, out_dir / "explain_after.txt")


if __name__ == "__main__":
    main()