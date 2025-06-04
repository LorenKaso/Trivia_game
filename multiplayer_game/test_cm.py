import socketio
import random
import time

sio = socketio.Client()
room_id = "test_room"
player_name = f"Player_{random.randint(1000, 9999)}"

@sio.event
def connect():
    print(f"✅ Connected to server as {player_name}")
    sio.emit("join_room", {"name": player_name, "room_id": room_id})

@sio.on("joined_room")
def on_joined(data):
    print(f"🏠 {data['message']}")

@sio.on("room_full")
def on_room_full(data):
    print("🚫 Room is full:", data["message"])

@sio.on("game_started")
def on_game_started(data):
    print("🚀 Game started!")

@sio.on("trivia_question")
def on_question(data):
    print(f"\n🧠 Question: {data['question']}")
    options = data["options"]
    for i, opt in enumerate(options):
        print(f"{chr(65+i)}) {opt}")
    
    # בוחר תשובה אקראית
    answer_letter = random.choice(['א', 'ב', 'ג', 'ד'])
    print(f"🗳 Sending answer: {answer_letter}")
    time.sleep(random.uniform(1, 3))  # חיקוי זמן תגובה אנושי
    sio.emit("submit_answer", {"room_id": room_id, "answer": answer_letter})

@sio.on("answer_summary")
def on_answer_summary(data):
    print(f"\n✅ Correct Answer: {data['correct_answer']}")
    print("📊 Scoreboard:")
    for entry in data["scoreboard"]:
        print(f" - {entry['name']}: {entry['score']} pts")

@sio.on("game_over")
def on_game_over(data):
    print("\n🎉 Game Over!")
    print(f"🏆 Winner: {data['winner']}")
    for entry in data["scores"]:
        print(f" - {entry['name']}: {entry['score']} pts")
    sio.disconnect()

@sio.event
def disconnect():
    print("❌ Disconnected from server")

# התחברות לשרת
sio.connect("http://localhost:5000")
sio.wait()
