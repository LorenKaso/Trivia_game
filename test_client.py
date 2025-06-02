import socketio
import random
import time

sio = socketio.Client()
score = 0
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
    global question_count
    question_count += 1

    question = data.get("question", "")
    options = data.get("options", [])
    correct_letter = data.get("correct", "")
    difficulty = data.get("difficulty", "?")

    print(f"\n🔹 Question {question_count} | Difficulty: {difficulty}")
    print(f"❓ {question}")
    for i, opt in enumerate(options):
        print(f"{i + 1}) {opt}")

    # קביעת איזו אפשרות היא הנכונה לפי האות
    hebrew_letters = ['א', 'ב', 'ג', 'ד']
    correct_index = hebrew_letters.index(correct_letter) if correct_letter in hebrew_letters else -1
    correct_text = options[correct_index] if 0 <= correct_index < len(options) else None

    # בחר תשובה – 60% סיכוי שתהיה נכונה
    if correct_text and random.random() < 0.6:
        answer = correct_text
    else:
        wrong_options = [opt for opt in options if opt != correct_text]
        answer = random.choice(wrong_options) if wrong_options else ""

    result_text = "✔️ Correct!" if answer == correct_text else "❌ Incorrect"

    print(f"🗳 Selected answer: {answer}")
    if correct_text:
        print(f"✅ Correct answer: {correct_text}")
        print(f"🎯 Result: {result_text}")

    # שמירת פרטי השאלה להדפסה בסוף
    received_questions.append({
        "number": question_count,
        "difficulty": difficulty,
        "question": question,
        "options": options,
        "selected": answer,
        "correct": correct_text,
        "result": result_text
    })

    time.sleep(1)
    sio.emit('submit_answer', {"answer": answer})

@sio.on('game_result')
def on_result(data):
    global score
    round_score = data.get("score", 0)
    score += round_score
    print(f"\n🏅 Score for this round: {round_score}")
    print(f"📊 Total score: {score}")

@sio.on('game_over')
def on_game_over(data):
    print(f"\n🏁 Game Over! Final Score: {data['final_score']}")
    print("\n📝 Summary of all questions:\n")

    for q in received_questions:
        print(f"🔹 Question {q['number']} (Difficulty {q['difficulty']})")
        print(f"❓ {q['question']}")
        for i, opt in enumerate(q['options']):
            print(f"  {i + 1}) {opt}")
        print(f"🗳 Selected: {q['selected']}")
        print(f"✅ Correct: {q['correct']}")
        print(f"🎯 Result: {q['result']}\n")

    sio.disconnect()

# התחברות לשרת
sio.connect('http://localhost:5000')
sio.wait()
