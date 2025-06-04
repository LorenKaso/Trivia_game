import random
import threading
import time
import uuid
from collections import defaultdict
from lifeline_manager import LifelineManager

class Player:
    def __init__(self, sid, name=""):
        self.sid = sid
        self.name = name
        self.score = 0
        self.answered = False
        self.answer_time = None
        self.current_answer = None
        self.lifelines = {
            "50_50": True,
            "call_a_friend": True,
            "double_score": True
        }

class GameRoom:
    def __init__(self, room_id, max_players=7, question_time=30):
        self.room_id = room_id
        self.players = {}
        self.max_players = max_players
        self.started = False
        self.current_question = None
        self.question_index = 0
        self.max_questions = 10
        self.question_timer = None
        self.question_time = question_time
        self.lock = threading.Lock()
        self.question_start_time = None
        self.lifeline_manager = LifelineManager()

    def add_player(self, sid, name):
        self.lifeline_manager.initialize_player(sid)
        if len(self.players) < self.max_players:
            player = Player(sid, name)
            self.players[sid] = player
            return True
        return False

    def remove_player(self, sid):
        if sid in self.players:
            del self.players[sid]

    def all_answered(self):
        return all(p.answered for p in self.players.values())

    def reset_answers(self):
        for player in self.players.values():
            player.answered = False
            player.answer_time = None
            player.current_answer = None

    def start_question_timer(self, on_timeout):
        if self.question_timer:
            self.question_timer.cancel()
        self.question_start_time = time.time()
        self.question_timer = threading.Timer(self.question_time, on_timeout)
        self.question_timer.start()

    def stop_timer(self):
        if self.question_timer:
            self.question_timer.cancel()
            self.question_timer = None

    def submit_answer(self, sid, answer):
        player = self.players.get(sid)
        if player and not player.answered:
            player.answered = True
            player.current_answer = answer
            player.answer_time = time.time() - self.question_start_time

    def calculate_scores(self, correct_answer):
        answered_correct = [p for p in self.players.values() if p.current_answer == correct_answer]
        answered_correct.sort(key=lambda p: p.answer_time)

        if answered_correct:
            for i, p in enumerate(answered_correct):
                base_score = 15 if i == 0 else 10 if i == 1 else 5
                final_score = base_score * 2 if self.used_double(p) else base_score
                p.score += final_score
                print(f"🏅 Player {p.sid} answered correctly! {'(Double Score)' if self.used_double(p) else ''} +{final_score} pts")

    def used_double(self, player):
        return hasattr(player, 'used_double_score') and player.used_double_score

    def mark_used_lifeline(self, sid, lifeline):
        if sid in self.players and self.players[sid].lifelines.get(lifeline):
            self.players[sid].lifelines[lifeline] = False
            if lifeline == "double_score":
                self.players[sid].used_double_score = True
            return True
        return False

# Dictionary to track all rooms
active_rooms = {}
