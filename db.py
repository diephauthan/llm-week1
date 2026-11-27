import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "cnc.db"

ROWS = [
    ("CNC-03", "end mill", "2026-11-17", 120, 790),
    ("CNC-03", "end mill", "2026-11-18", 140, 815),
    ("CNC-03", "end mill", "2026-11-19",  90, 860),
    ("CNC-05", "drill",    "2026-11-19",  60, 540),
]

def create_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DROP TABLE IF EXISTS runs")
    conn.execute("""
        CREATE TABLE runs (
        machine_id TEXT, tool_type TEXT, run_date TEXT,
        cutting_time_min REAL, mean_force_n REAL)""")
    conn.executemany("INSERT INTO runs VALUES (?, ?, ?, ?, ?)", ROWS)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()
    conn = sqlite3.connect(DB_PATH)
    for row in conn.execute("SELECT * FROM runs"):
        print(row)
    conn.close()