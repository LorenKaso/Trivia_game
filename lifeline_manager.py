import random

class LifelineManager:
    def __init__(self):
        self.lifelines = {}  # sid -> {"50_50": True, "call_a_friend": True, "double_score": True}

    def initialize_player(self, sid):
        self.lifelines[sid] = {
            "50_50": True,
            "call_a_friend": True,
            "double_score": True
        }

    def can_use(self, sid, lifeline_name):
        return self.lifelines.get(sid, {}).get(lifeline_name, False)

    def use(self, sid, lifeline_name):
        if self.can_use(sid, lifeline_name):
            self.lifelines[sid][lifeline_name] = False
            return True
        return False

    def get_available_lifelines(self, sid):
        return self.lifelines.get(sid, {})

    def apply_50_50(self, question_data):
        """Removes two wrong answers and returns reduced options"""
        correct = question_data["correct_answer"]
        options = question_data["options"]

        # האינדקס הנכון
        correct_index = ['א', 'ב', 'ג', 'ד'].index(correct)
        correct_option = options[correct_index]

        # הסר שתיים מתוך השגויות
        wrong_options = [opt for i, opt in enumerate(options) if i != correct_index]
        removed = random.sample(wrong_options, 2)
        reduced = [opt for opt in options if opt not in removed]
        return reduced
    
    def apply_call_a_friend(self, question_data):
        from llm_helpers import call_a_friend_suggestion
        return call_a_friend_suggestion(question_data)

    def apply_double_score(self, sid):
        if self.can_use(sid, "double_score"):
            self.use(sid, "double_score")
            return True
        return False

    def reset(self):
        self.lifelines = {}
