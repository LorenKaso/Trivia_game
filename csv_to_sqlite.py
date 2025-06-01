import sqlite3
import csv

# התחברות למסד הנתונים או יצירתו
conn = sqlite3.connect("trivia.db")
cursor = conn.cursor()

# מחיקה ויצירה מחדש של הטבלה
cursor.execute("DROP TABLE IF EXISTS trivia")
cursor.execute("""
    CREATE TABLE trivia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        option_a TEXT,
        option_b TEXT,
        option_c TEXT,
        option_d TEXT,
        correct_answer TEXT,
        difficulty INTEGER
    )
""")

# פתיחת קובץ ה-CSV וקריאה
with open("questions_cleaned.csv", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cursor.execute("""
            INSERT INTO trivia (question, option_a, option_b, option_c, option_d, correct_answer, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            row["question"],
            row["option_a"],
            row["option_b"],
            row["option_c"],
            row["option_d"],
            row["correct_answer"],
            int(row["difficulty"])
        ))

conn.commit()
conn.close()
print("✅ ייבוא השאלות למסד trivia.db הסתיים בהצלחה.")
