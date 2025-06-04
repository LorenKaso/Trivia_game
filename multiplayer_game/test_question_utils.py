import sys
import os

# הוספת הנתיב לתיקיית backend כך שנוכל לייבא את question_utils.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from question_utils import get_random_question

q = get_random_question()

if q:
    print("✅ שאלה נשלפה בהצלחה:")
    print("שאלה:", q["question"])
    print("תשובות:", q["options"])
    print("תשובה נכונה:", q["correct"])
else:
    print("❌ לא נמצאה שאלה")
