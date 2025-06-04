import sqlite3
import os

# נתיב יחסי אל trivia.db - שמניח שה-DB יושב בתוך תיקיית backend
DB_PATH = os.path.join(os.path.dirname(__file__), 'trivia.db')

def get_random_question():
    print(f"📂 Using DB Path: {DB_PATH}")  # רק לבדיקה
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT question, option_a, option_b, option_c, option_d, correct_answer 
        FROM trivia 
        ORDER BY RANDOM() 
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "question": row[0],
            "options": [row[1], row[2], row[3], row[4]],
            "correct": row[5]
        }
    return None
