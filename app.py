from flask import Flask, render_template, request, jsonify, redirect
import os
import sqlite3
import pandas as pd
from textblob import TextBlob
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
# --------------------------------------------------
# Flask App
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")
# --------------------------------------------------
# DATABASE
def get_connection():
    return sqlite3.connect(DATABASE)

def init_db():
    print("Initializing database...")
    conn = get_connection()
    """
    Create required tables if they don't exist.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS chats(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            emotion TEXT,
            risk TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
CREATE TABLE IF NOT EXISTS feedbacks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rating TEXT NOT NULL,
    feedback TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
    conn.commit()

    conn.close()
    print("Database initialized successfully.")
init_db()

GREETINGS = {
    "hi", "hello", "hey", "heyy", "hii",
    "good morning", "good afternoon", "good evening"
}

GOODBYES = {
    "bye", "goodbye", "see you", "take care", "see ya"
}

THANKS = {
    "thanks", "thank you", "thankyou", "thnx", "ty"
}
# --------------------------------------------------
# EMOTION DETECTION
HAPPY_WORDS = {
    "happy", "great", "awesome", "excellent", "amazing","fantastic", "wonderful", "good", "fine", "love", "joy", "cheerful", "grateful", "peaceful", "relaxed", "i am happy", "i'm happy", "i am fine", "i'm fine","feeling good","feeling great","feeling awesome","i feel happy","i feel good","i'm good","i am good","doing great","doing well","life is good",
}
SAD_WORDS = {
    "sad", "unhappy", "depressed", "hopeless", "cry", "crying", "alone", "lonely","worthless", "tired", "broken", "upset","heartbroken", "not happy", "not okay", "not ok","not good", "not fine", "i am unhappy", "i'm unhappy", "i am not happy", "i'm not happy", "feeling low","not feeling well","feeling bad","i feel bad","i feel sad","i am sad","i'm sad","i am depressed","i'm depressed","i am stressed","i'm stressed","not feeling good","feeling terrible","feeling awful","miserable","hurt","emotionally exhausted","mentally tired","mental stress","feeling lonely","feeling anxious", "stress", "stressed", "anxiety", "panic", "worried", "overthinking", "can't sleep", "cannot sleep", "want to die", "i want to die", "kill myself", "end my life", "suicide", "self harm", "don't want to live",
}
def detect_emotion(text):
    text = text.lower().strip()
    # Greetings / Thanks / Bye
    if any(word == text for word in GREETINGS):
        return "Greeting"
    if any(word == text for word in THANKS):
        return "Thanks"
    if any(word == text for word in GOODBYES):
        return "Goodbye"
    sad_phrases = [
"not feeling well","not feeling good","feeling bad","feeling low","feeling down","i feel bad","i feel sad","i am sad","i'm sad","i am depressed","i'm depressed","i feel lonely","i am lonely","i'm lonely","i am stressed","i'm stressed","i'm worried","i am worried","nobody understands me","nobody loves me","life is hard", "i hate myself","i feel worthless","i'm exhausted","mentally tired","die"
    ]
    happy_phrases = [
 "i am happy", "i'm happy", "feeling good", "feeling great","doing well","doing great","life is good","i got placed","i got internship","i got selected","i topped", "i passed","i'm excited","i am excited","today is amazing"
    ]
    if any(p in text for p in sad_phrases):
        return "Sad"
    if any(p in text for p in happy_phrases):
        return "Happy"
    has_happy = any(word in text for word in HAPPY_WORDS)
    has_sad = any(word in text for word in SAD_WORDS)
    if has_sad and not has_happy:
        return "Sad"
    if has_happy and not has_sad:
        return "Happy"
    polarity = TextBlob(text).sentiment.polarity
    if polarity >= 0.30:
        return "Happy"
    elif polarity <= -0.30:
        return "Sad"
    return "Neutral"
# --------------------------------------------------
# RISK DETECTION
def risk_level(text):

    text = text.lower().strip()
    critical_words = {
        "suicide","kill myself","end my life","want to die","i want to die","self harm","don't want to live","i wanna die"
    }
    high_words = {
        "depressed", "hopeless","worthless","panic","anxiety","crying", "can't sleep","cannot sleep""nobody understands me","nobody loves me","everyone hates me","i hate myself","i am worthless","i feel worthless","i am useless","i feel useless","i have no friends","i am alone", "i'm alone","i feel alone","nobody understands me","nobody loves me","life is hard","i feel hopeless","i am hopeless","i'm hopeless","i feel anxious","i am anxious","i'm anxious","i feel stressed","i am stressed","i'm stressed"
}
    moderate_words = {
        "sad","stress","stressed","lonely","alone","tired","broken","upset","worried", "overthinking","not feeling well","not feeling good","feeling low","feeling down","i failed","exam stress","work stress","bad relationship"
}
    if any(word in text for word in critical_words):
        return "Critical"
    if any(word in text for word in high_words):
        return "High"
    if any(word in text for word in moderate_words):
        return "Moderate"
    return "Low"
# --------------------------------------------------
# BOT RESPONSE
def generate_response(emotion, risk):
    if emotion == "Greeting":
        return (
        "Hello! 👋\n\n"
        "I'm MindCare AI.\n"
        "How are you feeling today?"
    )
    if emotion == "Thanks":
        return (
        "You're most welcome! 😊\n\n"
        "I'm always here whenever you need someone to talk to."
    )
    if emotion == "Goodbye":
       return (
        "Take care! 💙\n\n"
        "Remember to take care of yourself.\n"
        "Have a wonderful day!"
    )
    if risk == "Critical":
        return (
            "I'm really concerned about what you've shared. ❤️\n\n"
            "Please reach out to a trusted family member, friend, "
            "or a mental health professional as soon as possible. "
            "You don't have to go through this alone."
        )
    if risk == "High":
        return (
            "I'm sorry you're going through a difficult time. 💙\n\n"
            "Talking to someone you trust can really help. "
            "Remember, asking for help is a sign of strength."
        )
    if emotion == "Happy":
        return (
            "That's wonderful to hear! 😊\n\n"
            "Keep doing the things that make you happy and take care of yourself."
        )
    if emotion == "Sad":
        return (
            "I'm sorry you're feeling this way. 💙\n\n"
            "I'm here to listen. If you'd like, tell me a little more about what's bothering you."
        )
    return (
        "Thank you for sharing. 😊\n\n"
        "I'm here to listen whenever you need someone to talk to."
    )
# --------------------------------------------------
# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")
# --------------------------------------------------
# CHAT API
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()
    if message == "":
        return jsonify({
            "response": "Please enter a message.",
            "emotion": "Neutral",
            "risk": "Low"
        })
    emotion = detect_emotion(message)
    risk = risk_level(message)
    bot_response = generate_response(emotion, risk)
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO chats
        (message, response, emotion, risk)
        VALUES (?, ?, ?, ?)
    """, (
        message,
        bot_response,
        emotion,
        risk
    ))
    conn.commit()
    conn.close()
    return jsonify({
        "response": bot_response,
        "emotion": emotion,
        "risk": risk
    })
# --------------------------------------------------
# CHAT HISTORY
@app.route("/history")
def history():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT
            id,
            message,
            response,
            emotion,
            risk,
            created_at
        FROM chats
        ORDER BY id DESC
    """)
    chats = c.fetchall()
    conn.close()
    return render_template(
        "history.html",
        chats=chats
    )
# --------------------------------------------------
# DELETE SINGLE CHAT
@app.route("/delete/<int:id>")
def delete_chat(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "DELETE FROM chats WHERE id=?",
        (id,)
    )
    conn.commit()
    conn.close()
    return redirect("/history")
# --------------------------------------------------
# DASHBOARD
@app.route("/dashboard")
def dashboard():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM chats",
        conn
    )
    conn.close()
    total_messages = len(df)
    emotion_counts = {}
    risk_counts = {}
    if total_messages > 0:
        emotion_counts = (
            df["emotion"]
            .value_counts()
            .to_dict()
        )
        risk_counts = (
            df["risk"]
            .value_counts()
            .to_dict()
        )
        # Create Charts Folder
        os.makedirs("static/charts", exist_ok=True)
        # Emotion Chart
        plt.figure(figsize=(6,4))
        plt.bar(
            emotion_counts.keys(),
            emotion_counts.values(),
            color="#6366F1"
        )
        plt.title("Emotion Distribution")
        plt.xlabel("Emotion")
        plt.ylabel("Messages")
        plt.tight_layout()
        plt.savefig(
            "static/charts/emotion_chart.png",
            dpi=150,
            bbox_inches="tight"
        )
        plt.close()
        # Risk Chart
        plt.figure(figsize=(5,5))
        plt.pie(
            risk_counts.values(),
            labels=risk_counts.keys(),
            autopct="%1.1f%%",
            startangle=90
        )
        plt.title("Risk Distribution")
        plt.tight_layout()
        plt.savefig(
            "static/charts/risk_chart.png",
            dpi=150,
            bbox_inches="tight"
        )
        plt.close()
    # Dashboard Summary
    happy_count = emotion_counts.get("Happy", 0)
    sad_count = emotion_counts.get("Sad", 0)
    neutral_count = emotion_counts.get("Neutral", 0)
    low_count = risk_counts.get("Low", 0)
    moderate_count = risk_counts.get("Moderate", 0)
    high_count = risk_counts.get("High", 0)
    critical_count = risk_counts.get("Critical", 0)
    return render_template(
        "dashboard.html",
        total_messages=total_messages,
        emotion_counts=emotion_counts,
        risk_counts=risk_counts,
        happy_count=happy_count,
        sad_count=sad_count,
        neutral_count=neutral_count,
        low_count=low_count,
        moderate_count=moderate_count,
        high_count=high_count,
        critical_count=critical_count
    )
# --------------------------------------------------
# ABOUT PAGE
@app.route("/about")
def about():
    return render_template("about.html")
# --------------------------------------------------
# FEEDBACK PAGE
@app.route("/feedback")
def feedback():
    return render_template(
        "feedback.html",
        success=False
    )
    # --------------------------------------------------
# SUBMIT FEEDBACK
@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    name = request.form["name"]
    rating = request.form["rating"]
    feedback = request.form["feedback"]
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO feedbacks
        (name, rating, feedback)
        VALUES (?, ?, ?)
    """,
    (
        name,
        rating,
        feedback
    ))
    conn.commit()
    conn.close()
    return render_template(
        "feedback.html",
        success=True
    )
# --------------------------------------------------
# VIEW ALL FEEDBACKS
@app.route("/all_feedbacks")
def all_feedbacks():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT
            id,
            name,
            rating,
            feedback,
            created_at
        FROM feedbacks
        ORDER BY id DESC
    """)
    feedbacks = c.fetchall()
    conn.close()
    return render_template(
        "all_feedbacks.html",
        feedbacks=feedbacks
    )
# --------------------------------------------------
# CLEAR ALL CHAT HISTORY
@app.route("/clear")
def clear_history():
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM chats")
    conn.commit()
    conn.close()
    return redirect("/history")
# MAIN
import os

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)