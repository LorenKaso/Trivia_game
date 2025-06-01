import re
import csv

# קריאה מקובץ השאלות הגולמי
with open("questions_raw.txt", "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

questions = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    if "(קושי:" in line:
        try:
            question_match = re.match(r"^(.*)\(קושי: (\d+)\)", line)
            if not question_match:
                i += 1
                continue
            question = question_match.group(1).strip("? ").strip()
            difficulty = int(question_match.group(2))

            option_a = lines[i+1].strip()[2:].strip()
            option_b = lines[i+2].strip()[2:].strip()
            option_c = lines[i+3].strip()[2:].strip()
            option_d = lines[i+4].strip()[2:].strip()

            correct_line = lines[i+5].strip()
            correct_match = re.match(r"^תשובה: ([א-ד])\)", correct_line)
            correct = correct_match.group(1)

            questions.append({
                "question": question,
                "option_a": option_a,
                "option_b": option_b,
                "option_c": option_c,
                "option_d": option_d,
                "correct_answer": correct,
                "difficulty": difficulty
            })

            i += 7
        except:
            i += 1
    else:
        i += 1

# כתיבת הקובץ החדש
with open("questions_cleaned.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "question", "option_a", "option_b", "option_c", "option_d", "correct_answer", "difficulty"
    ])
    writer.writeheader()
    writer.writerows(questions)

print(f"✅ נוצרו {len(questions)} שאלות לקובץ questions_cleaned.csv")
