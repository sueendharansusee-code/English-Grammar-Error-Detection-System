"""
SQLite Database manager for English Grammar Error Detection System history tracking.
"""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "grammar_history.db")


def get_connection():
    """Establish and return SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create history table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            original_text TEXT NOT NULL,
            corrected_text TEXT NOT NULL,
            score INTEGER NOT NULL,
            error_count INTEGER NOT NULL,
            sentence_count INTEGER NOT NULL,
            word_count INTEGER NOT NULL,
            details_json TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_analysis(original_text, corrected_text, score, error_count, sentence_count, word_count, details):
    """Save an analysis report entry into SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    details_json = json.dumps(details)
    cursor.execute("""
        INSERT INTO history (original_text, corrected_text, score, error_count, sentence_count, word_count, details_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (original_text, corrected_text, score, error_count, sentence_count, word_count, details_json))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_all_history(limit=50):
    """Retrieve history records ordered by newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, original_text, corrected_text, score, error_count, sentence_count, word_count
        FROM history
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    history_list = []
    for row in rows:
        history_list.append({
            "id": row["id"],
            "timestamp": row["timestamp"],
            "original_text": row["original_text"],
            "corrected_text": row["corrected_text"],
            "score": row["score"],
            "error_count": row["error_count"],
            "sentence_count": row["sentence_count"],
            "word_count": row["word_count"]
        })
    return history_list


def get_history_by_id(record_id):
    """Retrieve full details of a specific history record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, original_text, corrected_text, score, error_count, sentence_count, word_count, details_json
        FROM history
        WHERE id = ?
    """, (record_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    return {
        "id": row["id"],
        "timestamp": row["timestamp"],
        "original_text": row["original_text"],
        "corrected_text": row["corrected_text"],
        "score": row["score"],
        "error_count": row["error_count"],
        "sentence_count": row["sentence_count"],
        "word_count": row["word_count"],
        "details": json.loads(row["details_json"])
    }


def clear_all_history():
    """Clear all entries in history table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history")
    conn.commit()
    conn.close()
