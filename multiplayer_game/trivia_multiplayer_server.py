import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room
from game_manager import GameRoom, active_rooms
from question_utils import get_random_question

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def on_connect():
    sid = request.sid
    print(f"📲 Player connected: {sid}")

@socketio.on('join_room')
def join_room_event(data):
    player_name = data['name']
    room_id = data['room_id']

    if room_id not in active_rooms:
        active_rooms[room_id] = GameRoom(room_id)

    room = active_rooms[room_id]
    success = room.add_player(sid=request.sid, name=player_name)

    if success:
        join_room(room_id)
        emit('joined_room', {'message': f"{player_name} joined room {room_id}"}, to=room_id)
    else:
        emit('room_full', {'message': 'Room is full'}, to=request.sid)

@socketio.on('start_game')
def start_game(data):
    room_id = data['room_id']
    question_time = data.get('question_time', 30)

    if room_id in active_rooms:
        room = active_rooms[room_id]
        room.question_time = question_time
        room.started = True
        socketio.emit('game_started', {}, to=room_id)
        send_next_question(room_id)

def send_next_question(room_id):
    room = active_rooms[room_id]
    if room.question_index >= room.max_questions:
        end_game(room_id)
        return

    room.current_question = get_random_question()
    room.question_index += 1
    room.reset_answers()

    socketio.emit('trivia_question', {
        'question': room.current_question['question'],
        'options': room.current_question['options']
    }, to=room_id)

    def timeout_handler():
        print(f"⏰ Timeout for room {room_id}, processing answers...")
        finalize_question(room_id)

    room.start_question_timer(timeout_handler)

def finalize_question(room_id):
    room = active_rooms[room_id]
    room.stop_timer()
    correct_answer = room.current_question['correct']
    room.calculate_scores(correct_answer)

    scoreboard = [
        {"name": p.name, "score": p.score}
        for p in room.players.values()
    ]

    socketio.emit('answer_summary', {
        'correct_answer': correct_answer,
        'scoreboard': scoreboard
    }, to=room_id)

    socketio.sleep(3)  # תן זמן לראות את התוצאה
    send_next_question(room_id)

def end_game(room_id):
    room = active_rooms[room_id]
    scores = sorted(room.players.values(), key=lambda p: p.score, reverse=True)
    winner = scores[0].name if scores else "No one"

    socketio.emit('game_over', {
        'winner': winner,
        'scores': [{"name": p.name, "score": p.score} for p in scores]
    }, to=room_id)

@socketio.on('submit_answer')
def submit_answer(data):
    sid = request.sid
    room_id = data['room_id']
    answer = data['answer']

    if room_id in active_rooms:
        room = active_rooms[room_id]
        room.submit_answer(sid, answer)

        if room.all_answered():
            finalize_question(room_id)

@socketio.on('use_lifeline')
def use_lifeline(data):
    sid = request.sid
    room_id = data['room_id']
    lifeline = data['lifeline']

    if room_id in active_rooms:
        room = active_rooms[room_id]
        player = room.players.get(sid)

        if lifeline == "50_50":
            if room.lifeline_manager.use(sid, "50_50"):
                reduced_options = room.lifeline_manager.apply_50_50(room.current_question)
                emit("lifeline_used", {"lifeline": "50_50", "options": reduced_options}, to=sid)

        elif lifeline == "call_a_friend":
            if room.lifeline_manager.use(sid, "call_a_friend"):
                suggestion = room.lifeline_manager.apply_call_a_friend(room.current_question)
                emit("lifeline_used", {"lifeline": "call_a_friend", "suggestion": suggestion}, to=sid)

        elif lifeline == "double_score":
            if room.lifeline_manager.apply_double_score(sid):
                player.used_double_score = True
                print(f"🔥 DOUBLE SCORE USED by {sid}")
                emit("lifeline_used", {"lifeline": "double_score"}, to=sid)

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    for room in active_rooms.values():
        room.remove_player(sid)

if __name__ == '__main__':
    print("🎮 Multiplayer Trivia Server running on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000)
