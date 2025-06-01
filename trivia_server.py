import random
import sqlite3
from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

def get_random_question():
    conn = sqlite3.connect("trivia.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, option_a, option_b, option_c, option_d, correct_answer FROM trivia ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "question": row[0],
            "options": [row[1], row[2], row[3], row[4]],
            "correct": row[5]  # לשימוש פנימי לציון
        }
    return None

# זיכרון של ניקוד לדוגמה
scores = {}

@socketio.on('connect')
def handle_connect():
    print("📲 Client connected")
    question = get_random_question()
    print("🎲 שאלה שנבחרה:", question)
    if question:
        emit('trivia_question', {
            "question": question["question"],
            "options": question["options"]
        })
        # שמירה של תשובה נכונה לשימוש בהמשך
        scores['correct_answer'] = question["correct"]
    else:
        emit('trivia_question', {"question": "לא נמצאה שאלה 😢", "options": []})

@socketio.on('submit_answer')
def handle_answer(data):
    print(f"📥 Received answer: {data['answer']}")
    correct = scores.get('correct_answer')
    score = 10 if data["answer"] == correct else 0
    emit('game_result', {"score": score})
    print(f"🏆 Score: {score}")

if __name__ == '__main__':
    print("🎮 Trivia server running on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000)
