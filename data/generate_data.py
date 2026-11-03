import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

N_OPERATORS = 20
N_CALLS = 5000
DAYS = 30
START = datetime(2026, 10, 1)

# --- Операторы ---
teams = ["A", "B", "C"]
operators = pd.DataFrame({
    "operator_id": range(1, N_OPERATORS + 1),
    "name": [f"Operator_{i:02d}" for i in range(1, N_OPERATORS + 1)],
    "team_id": [teams[i % 3] for i in range(N_OPERATORS)],
    "hire_date": [START - timedelta(days=random.randint(30, 365))
                  for _ in range(N_OPERATORS)],
})

# --- Звонки (с намеренными аномалиями) ---
rows = []
for call_id in range(1, N_CALLS + 1):
    op_id = random.randint(1, N_OPERATORS)
    day = random.randint(0, DAYS - 1)
    start = START + timedelta(days=day, hours=random.randint(8, 20),
                              minutes=random.randint(0, 59))

    duration = max(30, int(np.random.normal(300, 120)))
    wait = int(np.random.exponential(20))

    # 3% звонков — аномально длинная пауза (редкое явление)
    if random.random() < 0.03:
        wait = random.randint(150, 400)

    # 10% — сброшенные звонки
    status = "dropped" if random.random() < 0.10 else "completed"

    # Оценка клиента
    rating = None if status == "dropped" else int(np.random.choice(
        [1, 2, 3, 4, 5], p=[0.05, 0.08, 0.15, 0.37, 0.35]
    ))

    rows.append({
        "call_id": call_id,
        "operator_id": op_id,
        "client_id": random.randint(1, 1000),
        "start_time": start,
        "duration_sec": duration,
        "wait_time_sec": wait,
        "status": status,
        "rating": rating,
    })

calls = pd.DataFrame(rows)

out = Path(__file__).parent
operators.to_csv(out / "operators.csv", index=False)
calls.to_csv(out / "calls.csv", index=False)
print(f"✔ Generated {len(operators)} operators and {len(calls)} calls")