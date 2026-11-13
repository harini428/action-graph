import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def init_db():
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                transcript LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                meeting_id INT NOT NULL,
                type VARCHAR(50),
                task TEXT,
                owner VARCHAR(100),
                deadline VARCHAR(100),
                needs_review TINYINT(1) DEFAULT 0,
                status VARCHAR(20) DEFAULT 'open',
                FOREIGN KEY (meeting_id) REFERENCES meetings(id)
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_meeting(title, transcript, items):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO meetings (title, transcript) VALUES (%s, %s)",
            (title, transcript),
        )
        meeting_id = cur.lastrowid
        for it in items:
            cur.execute(
                "INSERT INTO items (meeting_id, type, task, owner, deadline, needs_review) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    meeting_id,
                    it.get("type", "unknown"),
                    it.get("task", ""),
                    it.get("owner", "unknown"),
                    it.get("deadline", "unknown"),
                    1 if it.get("needs_review") else 0,
                ),
            )
        conn.commit()
        return meeting_id
    finally:
        conn.close()


def get_items(meeting_id):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM items WHERE meeting_id = %s", (meeting_id,))
        return cur.fetchall()
    finally:
        conn.close()
def get_all_items(only_review=False):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        sql = (
            "SELECT i.id, i.type, i.task, i.owner, i.deadline, "
            "i.needs_review, i.status, m.title AS meeting_title "
            "FROM items i JOIN meetings m ON i.meeting_id = m.id"
        )
        if only_review:
            sql += " WHERE i.needs_review = 1"
        sql += " ORDER BY i.id DESC"
        cur.execute(sql)
        return cur.fetchall()
    finally:
        conn.close()


def mark_done(item_id):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE items SET status = 'done' WHERE id = %s", (item_id,))
        conn.commit()
    finally:
        conn.close()
def get_item(item_id):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
        return cur.fetchone()
    finally:
        conn.close()


def approve_item(item_id):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE items SET needs_review = 0 WHERE id = %s", (item_id,))
        conn.commit()
    finally:
        conn.close()


def update_item(item_id, owner, deadline):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE items SET owner = %s, deadline = %s, needs_review = 0 WHERE id = %s",
            (owner, deadline, item_id),
        )
        conn.commit()
    finally:
        conn.close()

