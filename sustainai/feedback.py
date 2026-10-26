"""Local SQLite inspection log. No automatic model retraining or valve control."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

STATES = ['New', 'Acknowledged', 'Inspected', 'Resolved']
OUTCOMES = ['Pending', 'Confirmed leak', 'Legitimate usage', 'Sensor fault', 'Inconclusive']

def connect(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, ticket TEXT, status TEXT, outcome TEXT, notes TEXT, updated TEXT)')
    return db

def history(path):
    with connect(path) as db:
        return db.execute('SELECT ticket,status,outcome,notes,updated FROM events ORDER BY id').fetchall()

def update(path, ticket, status, outcome, notes):
    if status not in STATES or outcome not in OUTCOMES: raise ValueError('Invalid inspection value.')
    if not ticket or len(ticket)>200 or len(notes)>1000: raise ValueError('Invalid ticket or note length.')
    with connect(path) as db:
        prev = db.execute('SELECT status FROM events WHERE ticket=? ORDER BY id DESC LIMIT 1', (ticket,)).fetchone()
        old = prev[0] if prev else 'New'
        if STATES.index(status) < STATES.index(old) or STATES.index(status) > STATES.index(old)+1:
            raise ValueError('Move one step forward: New > Acknowledged > Inspected > Resolved.')
        if status in ['Inspected', 'Resolved'] and (outcome=='Pending' or not notes.strip()):
            raise ValueError('Inspection and resolution require an outcome and inspection notes.')
        if status=='Resolved' and outcome=='Inconclusive': raise ValueError('Inconclusive cases must remain under inspection.')
        db.execute('INSERT INTO events(ticket,status,outcome,notes,updated) VALUES(?,?,?,?,?)',
                   (ticket,status,outcome,notes.strip(),datetime.now(timezone.utc).isoformat()))
