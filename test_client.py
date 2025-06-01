import socketio
import time

sio = socketio.Client()

@sio.event
def connect():
    print("✅ Connected to server")

@sio.event
def disconnect():
    print("❌ Disconnected from server")

@sio.event
def trivia_question(data):
    print(f"\n🧠 Question: {data['question']}")
    for i, option in enumerate(data['options'], start=1):
        print(f"{i}) {option}")
    
    # מדמה בחירה אקראית בתשובה לאחר המתנה קצרה
    time.sleep(2)
    selected_answer = data['options'][0]  # נניח תמיד בוחר באופציה הראשונה
    sio.emit("submit_answer", {
        "answer": selected_answer
    })

@sio.event
def game_result(data):
    print(f"\n🏁 Game Over! Final Score: {data['score']}")

# התחברות לשרת
sio.connect("http://localhost:5000")

# שמירה על חיבור חי עד עצירה
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    sio.disconnect()
