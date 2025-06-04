import os
import openai
from dotenv import load_dotenv

# טען משתני סביבה מקובץ .env
load_dotenv()

# קבע את מפתח ה-API של OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in environment variables (.env)")

# הגדר את לקוח ה-API של OpenAI
client = openai.OpenAI(api_key=openai_api_key)

def call_a_friend_suggestion_openai(question_data, correct_answer):
    """
    מקבל שאלה + אפשרויות, ומחזיר תשובת LLM בסגנון 'עזרת חבר'.
    במקרה של כשל, תחזיר את התשובה הנכונה (fallback).
    """
    prompt_message = f"""You're a helpful and fun trivia expert.
    Question: {question_data['question']}
    Options: {', '.join(question_data['options'])}
    Suggest the most likely correct answer in one short sentence, and add a light-hearted tone."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful and fun trivia expert."},
                {"role": "user", "content": prompt_message}
            ],
            max_tokens=100,
            temperature=0.7,
        )
        # אם ה-LLM ענה בהצלחה, נחזיר את תשובתו
        return response.choices[0].message.content.strip()

    except openai.APIError as e:
        print(f"❌ Error with OpenAI API: {e}")
        # אם יש שגיאת API, נחזיר את התשובה הנכונה כ-fallback
        print(f"✅ Fallback to correct answer: {correct_answer}")
        return f"אוף, חבר ה-AI לא ענה. אבל התשובה הנכונה היא: {correct_answer}!"
    except Exception as e:
        print(f"❌ General error: {e}")
        # אם יש שגיאה כללית אחרת, גם כן נחזיר את התשובה הנכונה
        print(f"✅ Fallback to correct answer: {correct_answer}")
        return f"מצטער, הייתה תקלה! התשובה הנכונה היא: {correct_answer}."

# 🔁 בדיקה ידנית
if __name__ == "__main__":
    test_question_1 = {
        "question": "What is the capital of Japan?",
        "options": ["Seoul", "Beijing", "Tokyo", "Bangkok"]
    }
    correct_answer_1 = "Tokyo" # הוסף את התשובה הנכונה כאן

    print("📞 Call-a-friend response (OpenAI with fallback):")
    # נשלח את השאלה ואת התשובה הנכונה
    print(call_a_friend_suggestion_openai(test_question_1, correct_answer_1))

    print("-" * 30) # קו הפרדה

    test_question_2 = {
        "question": "Which animal is known for its long neck?",
        "options": ["Elephant", "Giraffe", "Tiger", "Kangaroo"]
    }
    correct_answer_2 = "Giraffe" # הוסף את התשובה הנכונה כאן

    print("\n📞 Call-a-friend response (OpenAI with fallback):")
    print(call_a_friend_suggestion_openai(test_question_2, correct_answer_2))