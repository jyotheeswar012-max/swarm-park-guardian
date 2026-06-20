import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "data/missions.db"

class Hub:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS missions (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                drone_id  INTEGER,
                task_type TEXT,
                location  TEXT,
                status    TEXT
            )
        """)
        conn.commit()
        conn.close()

    def log_task(self, drone_id: int, task_type: str, location: tuple, status: str):
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO missions (timestamp, drone_id, task_type, location, status) VALUES (?,?,?,?,?)",
            (datetime.now().isoformat(), drone_id, task_type, json.dumps(location), status)
        )
        conn.commit()
        conn.close()

    def get_all_missions(self) -> list:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("SELECT * FROM missions ORDER BY id DESC LIMIT 100").fetchall()
        conn.close()
        return [{"id": r[0], "timestamp": r[1], "drone_id": r[2],
                 "task_type": r[3], "location": json.loads(r[4]), "status": r[5]}
                for r in rows]
