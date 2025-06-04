from flask import Flask, request
from flask_socketio import SocketIO, emit
import sqlite3
import random
import threading
from llm_helpers import call_a_friend_suggestion

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

def handle_timeout(sid):
    game = active_games.get(sid)
    if game and not game.get("answered"):
        print(f"⏰ Timeout for client {sid}, moving to next question...")
        handle_answer({"answer": None}, sid=sid, timed_out=True)

def send_next_question(sid):
    game = active_games[sid]
    question_data = get_random_question()
    if question_data:
        game["current_question"] = question_data
        game["answered"] = False  # שחקן טרם ענה

        socketio.emit('trivia_question', {
            "question": question_data["question"],
            "options": question_data["options"],
            "correct": question_data["correct"],
            "difficulty": question_data["difficulty"]
        }, to=sid)

        # הפעל טיימר של 20 שניות
        timer = threading.Timer(20.0, handle_timeout, args=(sid,))
        game["timer"] = timer
        timer.start()
    else:
        socketio.emit('game_over', {"final_score": game["score"]}, to=sid)

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

@socketio.on('use_lifeline')
def handle_lifeline(data):
    sid = request.sid
    lifeline = data.get("lifeline")

    if lifeline == "call_a_friend":
        game = active_games.get(sid)
        if not game:
            return
        
        question_data = game.get("current_question")
        if not question_data:
            return

        try:
            suggestion = call_a_friend_suggestion(question_data)
        except Exception as e:
            print(f"❌ Error with LLM lifeline: {e}")
            suggestion = "Sorry, your friend didn’t answer. Maybe they're on vacation 🌴."

        socketio.emit('lifeline_response', {
            "lifeline": "call_a_friend",
            "message": suggestion
        }, to=sid)

@socketio.on('submit_answer')
def handle_answer(data, sid=None, timed_out=False):
    if sid is None:
        sid = request.sid

    game = active_games.get(sid)
    if not game:
        return

    # בטל את הטיימר
    timer = game.get("timer")
    if timer:
        timer.cancel()

    game["answered"] = True  # שחקן ענה או עבר הזמן

    player_answer = data.get("answer")
    correct_answer = game["current_question"]["correct"]

    score_this_round = 0
    if player_answer == correct_answer:
        score_this_round = 10
        game["score"] += score_this_round
        result = "✔️ Correct!"
    elif timed_out:
        result = "⏰ Timeout! No answer submitted."
    else:
        result = "❌ Incorrect"

    socketio.emit("answer_result", {
        "correct": correct_answer,
        "result": result,
        "score_this_round": score_this_round,
        "total_score": game["score"]
    }, to=sid)

    game["questions_asked"] += 1
    if game["questions_asked"] >= game["max_questions"]:
        socketio.emit("game_over", {"final_score": game["score"]}, to=sid)
        del active_games[sid]
    else:
        send_next_question(sid)

if __name__ == '__main__':
    print("🎮 Trivia server running on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000)