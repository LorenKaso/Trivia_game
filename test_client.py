import socketio
import random
import time
import os
import threading
import datetime

def load_total_score():
    if os.path.exists("score.txt"):
        with open("score.txt", "r") as f:
            return int(f.read().strip())
    return 0

def save_total_score(score):
    with open("score.txt", "w") as f:
        f.write(str(score))

score = load_total_score()

countdown_stop_event = threading.Event()

def countdown(seconds):
    for i in range(seconds, 0, -1):
        if countdown_stop_event.is_set():
            break
        print(f"⏳ Time left: {i} seconds", end="\r")
        time.sleep(1)

sio = socketio.Client()
question_count = 0
MAX_QUESTIONS = 10
received_questions = []  # רשימה של כל השאלות

@sio.event
def connect():
    print("✅ Connected to server")

@sio.event
def disconnect():
    print("❌ Disconnected from server")

@sio.on('trivia_question')
def on_question(data):
    global question_count, countdown_stop_event
    question_count += 1

    question = data.get("question", "")
    options = data.get("options", [])
    correct_letter = data.get("correct", "")  # זו האות הנכונה (א, ב, ג, ד)
    difficulty = data.get("difficulty", "?")

    print(f"\n🔹 Question {question_count} | Difficulty: {difficulty}")
    print(f"❓ {question}")
    for i, opt in enumerate(options):
        print(f"{i + 1}) {opt}")

    # קביעת איזו אפשרות היא הנכונה לפי האות
    hebrew_letters = ['א', 'ב', 'ג', 'ד']
    correct_index = hebrew_letters.index(correct_letter) if correct_letter in hebrew_letters else -1
    correct_text = options[correct_index] if 0 <= correct_index < len(options) else None

    selected_text_answer = ""
    selected_letter_answer = ""

    # בחר תשובה – 60% סיכוי שתהיה נכונה
    if correct_text and random.random() < 0.6:
        selected_text_answer = correct_text
        selected_letter_answer = correct_letter
    else:
        wrong_options = [opt for opt in options if opt != correct_text]
        if wrong_options:
            selected_text_answer = random.choice(wrong_options)
            selected_letter_answer = hebrew_letters[options.index(selected_text_answer)]
        else:
            selected_text_answer = ""
            selected_letter_answer = ""

    result_text = "✔️ Correct!" if selected_text_answer == correct_text else "❌ Incorrect"

    print(f"🗳 Selected answer: {selected_text_answer}")
    if correct_text:
        print(f"✅ Correct answer: {correct_text}")
        print(f"🎯 Result: {result_text}")

    # שמירת פרטי השאלה
    received_questions.append({
        "number": question_count,
        "difficulty": difficulty,
        "question": question,
        "options": options,
        "selected": selected_text_answer,
        "correct": correct_text,
        "result": result_text
    })

    # 🕒 ספירה לאחור עם עצירה אם השחקן עונה
    countdown_stop_event.clear()
    threading.Thread(target=countdown, args=(20,)).start()

    # ⏱ סימולציה של זמן תגובה של השחקן (רנדומלי)
    time.sleep(random.randint(1, 4))

    # עצור את הספירה ושלח תשובה
    countdown_stop_event.set()
    sio.emit('submit_answer', {"answer": selected_letter_answer})

@sio.on('lifeline_response')
def on_lifeline_response(data):
    if data["lifeline"] == "call_a_friend":
        print(f"\n📞 Call-a-friend says: {data['message']}")

@sio.on('answer_result')
def on_answer_result(data):
    global score
    round_score = data.get("score_this_round", 0)
    current_total_score = data.get("total_score", score) # קראתי לזה current_total_score כדי למנוע בלבול עם המשתנה הגלובלי score
    score = current_total_score # עדכן את המשתנה הגלובלי score

    save_total_score(score) # שמור את הניקוד הכולל לקובץ

    print(f"🏅 Score for this round: {round_score}")
    print(f"📊 Total score after this question: {score}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # ✅ כאן התיקון: שמור את הניקוד עבור הסיבוב והניקוד הכולל
    # בתוך אובייקט השאלה האחרון ברשימת received_questions
    if received_questions: # ודא שיש שאלות ברשימה
        received_questions[-1]["round_score"] = round_score
        received_questions[-1]["total_score_after"] = current_total_score # או score

@sio.on('game_result')
def on_result(data):
    global score
    round_score = data.get("score", 0)
    score += round_score
    print(f"\n🏅 Score for this round: {round_score}")
    print(f"📊 Total score: {score}")

    # ⬅️ שמירת הניקוד בתוך השאלה האחרונה שהתקבלה
    if received_questions:
        received_questions[-1]["round_score"] = round_score
        received_questions[-1]["total_score_after"] = score


@sio.on('game_over')
def on_game_over(data):
    print(f"\n🏁 Game Over! Final Score: {data['final_score']}")
    print("\n📝 Summary of all questions:\n")

    for q in received_questions:
        print(f"🔹 Question {q['number']} (Difficulty {q['difficulty']})")
        print(f"❓ {q['question']}")
        for i, opt in enumerate(q['options']):
            print(f"   {i + 1}) {opt}")
        print(f"🗳 Selected: {q['selected']}")
        print(f"✅ Correct: {q['correct']}")
        print(f"🎯 Result: {q['result']}")
        # ⬅️ עכשיו הערכים האלה צריכים להיות זמינים ב-q
        print(f"🏅 Score for this round: {q.get('round_score', 0)}")
        print(f"📊 Total score after this question: {q.get('total_score_after', 0)}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    save_total_score(score)
    sio.disconnect()

# התחברות לשרת
sio.connect('http://localhost:5000')
sio.wait()