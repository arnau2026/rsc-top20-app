# auth.py
import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect("users.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT
)
""")
conn.commit()

def register_user(email, password):
    try:
        cur.execute(
            "INSERT INTO users VALUES (?, ?)",
            (email, hash_password(password))
        )
        conn.commit()
        return True
    except:
        return False

def login_user(email, password):
    cur.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, hash_password(password))
    )
    return cur.fetchone() is not None