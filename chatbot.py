import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import streamlit as st
import random

nltk.download('popular', quiet=True)

# Load the CSV file
file_path = os.path.join(os.getcwd(), "aimedchatbot.csv")
data = pd.read_csv(file_path)

# Convert all data to strings and fill NaN values with empty strings
data = data.astype(str).fillna('')

# Prepare the data
sent_tokens = data['Question'].tolist()  # List of all questions in the dataset
answers = data['Answer'].tolist()  # List of all corresponding answers

# Greeting inputs and responses
GREETING_INPUTS = ("hello", "hi", "hey", "sup", "what's up")
GREETING_RESPONSES = ["Hi there!", "Hello!", "Hey!", "Hi! How can I assist you today?"]

def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)
    return None

# Function to get the response from CSV
def get_response(question):
    # Check if the question is a greeting
    greeting_response = greeting(question)
    if greeting_response:
        return greeting_response

    # Attempt to match with questions in the CSV using cosine similarity
    question = question.lower()
    sent_tokens.append(question)  # Add user question to token list for TF-IDF comparison

    # Generate TF-IDF vectors
    TfidfVec = TfidfVectorizer(stop_words='english')  # Removed tokenizer parameter to avoid conflict
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf[:-1])  # Exclude user question for comparison
    idx = vals.argsort()[0][-1]  # Index of the best match
    max_similarity = vals[0][idx]  # Highest similarity score

    # Remove user input from sent_tokens to avoid duplicate handling
    sent_tokens.pop()

    # If a match is found in the CSV, return the corresponding answer
    if max_similarity > 0.2:  # Adjust threshold as needed
        return answers[idx]

    # If no match, fallback response
    return "I’m sorry, I don’t have enough information to answer that. Could you please rephrase?"

# Daily health tip function
def get_daily_health_tip():
    health_tips = [
        "Drink plenty of water throughout the day to stay hydrated 💧",
        "Make sure to get at least 30 minutes of physical activity daily 💪",
        "Eat a balanced diet with plenty of fruits and vegetables 🍏",
        "Don't forget to take regular breaks if you're working or studying! 🧘",
        "Get a good night's sleep for at least 7-8 hours 🛏️"
    ]
    
    # Ensure the health tips list is not empty
    if health_tips:
        return random.choice(health_tips)
    else:
        return "Take care of yourself today!"

# Streamlit main function
def main():
    # Set page configuration with custom color and icon
    st.set_page_config(page_title="MedBot: Your Personal Health Assistant", page_icon="💬", layout="wide")

    # Custom header with color and styling
    st.markdown("""
    <style>
        .header {
            color: #FF6347;
            font-size: 40px;
            font-weight: bold;
            text-align: center;
        }
        .tip {
            font-size: 20px;
            color: #2E8B57;
        }
        .conversation {
            background-color: #F0F8FF;
            padding: 10px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .bot {
            color: #008080;
            font-weight: bold;
        }
        .user {
            color: #1E90FF;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

    # Display Chatbot title with color
    st.markdown('<p class="header">MedBot: Your Personal Health Assistant</p>', unsafe_allow_html=True)

    # Display a health tip at the start
    st.subheader("🌿 Health Tip of the Day:")
    st.write(get_daily_health_tip())

    # Initialize session state to hold conversation (for displaying only latest response)
    if "latest_answer" not in st.session_state:
        st.session_state.latest_answer = ""

    # User input
    user_input = st.text_input("You: ", "")

    if user_input:
        # Get and display bot's response
        response_text = get_response(user_input)
        st.session_state.latest_answer = response_text

    # Display the most recent answer from the bot
    if st.session_state.latest_answer:
        st.markdown(f'<div class="bot">MedBot: {st.session_state.latest_answer}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
