from flask import Flask, request
from flask_socketio import SocketIO, emit
import sqlite3
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# ✅ כאן נגדיר את מילון המשחקים הפעילים
active_games = {}

def get_random_question():
    conn = sqlite3.connect("trivia.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, option_a, option_b, option_c, option_d, correct_answer, difficulty FROM trivia ORDER BY RANDOM() LIMIT 1")    
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "question": row[0],
            "options": [row[1], row[2], row[3], row[4]],
            "correct": row[5],
            "difficulty": row[6] 
        }
    return None

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    print(f"📲 Client connected: {sid}")
    active_games[sid] = {
        "score": 0,
        "questions_asked": 0,
        "max_questions": 10
    }
    
    send_next_question(sid)

def send_next_question(sid):
    game = active_games[sid]
    question_data = get_random_question()
    if question_data:
        game["current_question"] = question_data
        emit('trivia_question', {
            "question": question_data["question"],
            "options": question_data["options"],
            "correct": question_data["correct"],
            "difficulty": question_data["difficulty"]        }, to=sid)
    else:
        emit('game_over', {"final_score": game["score"]}, to=sid)

@socketio.on('submit_answer')
def handle_answer(data):
    sid = request.sid
    game = active_games[sid]
    player_answer = data.get("answer")
    correct_answer = game["current_question"]["correct"]

    # הגדר את score_this_round כאן, לפני בלוק ה-if/else
    score_this_round = 0 # אתחל ל-0 כברירת מחדל

    if player_answer == correct_answer:
        score_this_round = 10 # הקצה ערך למשתנה שהוגדר מחוץ לבלוק
        game["score"] += score_this_round # השתמש ב-score_this_round כאן
        result = "✔️ Correct!"
    else:
        # אם התשובה שגויה, score_this_round יישאר 0 (מהאתחול)
        result = "❌ Incorrect"

    socketio.emit("answer_result", {
        "correct": correct_answer,
        "result": result,
        "score_this_round": score_this_round,  # עכשיו זה מתייחס לניקוד הנכון לסיבוב
        "total_score": game["score"]
    }, to=sid)

    game["questions_asked"] += 1
    if game["questions_asked"] >= game["max_questions"]:
        emit("game_over", {"final_score": game["score"]}, to=sid)
        del active_games[sid]
    else:
        send_next_question(sid)

if __name__ == '__main__':
    print("🎮 Trivia server running on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000)