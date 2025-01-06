import streamlit as st
import pyrebase
from huggingface_hub import InferenceClient
import requests
import json
import PyPDF2

# Firebase Configuration
firebase_config = {
    "apiKey": st.secrets["firebase"]["apiKey"],
    "authDomain": st.secrets["firebase"]["authDomain"],
    "projectId": st.secrets["firebase"]["projectId"],
    "storageBucket": st.secrets["firebase"]["storageBucket"],
    "messagingSenderId": st.secrets["firebase"]["messagingSenderId"],
    "appId": st.secrets["firebase"]["appId"],
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "conversations" not in st.session_state:
    st.session_state.conversations = []

# CSS Styling
st.markdown(
    """
    <style>
    .fixed-container {
        display: flex;
        flex-direction: column;
        height: 100vh;
        justify-content: space-between;
    }
    .chat-container {
        flex: 1;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: #f9f9f9;
    }
    .input-container {
        width: 100%;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Helper Functions
def register_user(email, password, confirm_password):
    if password != confirm_password:
        st.error("Passwords do not match!")
        return
    try:
        user = auth.create_user_with_email_and_password(email, password)
        st.success("Registration successful! Please log in.")
    except Exception as e:
        st.error(f"Error: {e}")


def login_user(email, password, placeholder):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state.logged_in = True
        st.session_state.user_email = email
        st.session_state.conversations = []
        st.success(f"Welcome, {email}!")
        placeholder.empty()
        chatbot_ui(placeholder)
    except Exception as e:
        st.error(f"Error: {e}")


def login_ui(placeholder):
    with placeholder.container():
        st.header("Welcome to Medi Bot 🤖")
        action = st.radio("Select Action", ["Login", "Register", "Guest Login"], horizontal=True)

        if action == "Register":
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            if st.button("Register"):
                register_user(email, password, confirm_password)

        elif action == "Login":
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                login_user(email, password, placeholder)

        elif action == "Guest Login":
            if st.button("Enter as Guest"):
                st.session_state.logged_in = True
                st.session_state.user_email = "Guest"
                st.session_state.conversations = []
                st.success("Logged in as Guest 🎉")
                placeholder.empty()
                chatbot_ui(placeholder)


def chatbot_ui(placeholder):
    with placeholder.container():
        st.sidebar.success(f"Logged in as {st.session_state.user_email}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.conversations = []
            placeholder.empty()
            login_ui(placeholder)

        st.header("Medi Bot 🤖")
        st.caption("Your personalized medical assistant.")

        available_models = [
            "gemma-mental-health-fine-tune",
            "Mistral-1.5B-medical-QA",
            "llama-3.2-1B-Lora-Fine_Tune-FineTome",
        ]

        selected_model = st.selectbox("Choose a model:", available_models)

        chat_container = st.empty()
        with st.container():
            user_input = st.text_input("Your message:", placeholder="Type your query here...")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Generate Response"):
                    if user_input.strip():
                        try:
                            response = None
                            query = f"Medical assistant:\n\n{user_input}"

                            # Removed the PDF context handling for the Gemini model
                            
                            # Now, process the query based on selected model
                            if selected_model == "Mistral-1.5B-medical-QA":
                                # Replace this with your call to the selected model
                                response = "Mistral model response here."

                            elif selected_model == "gemma-mental-health-fine-tune":
                                response = "Gemma mental health fine-tuned model response here."

                            elif selected_model == "llama-3.2-1B-Lora-Fine_Tune-FineTome":
                                response = "Llama fine-tuned model response here."

                            st.session_state.conversations.append({"query": user_input, "response": response})

                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Please enter a message.")
            with col2:
                if st.button("Clear Conversation History"):
                    st.session_state.conversations = []
                    st.success("Conversation history cleared.")

        with chat_container.container():
            if st.session_state.conversations:
                st.subheader("🖋 Conversation History")
                for convo in st.session_state.conversations:
                    st.markdown(f"**You:** {convo['query']}")
                    st.markdown(f"**Medi Bot:** {convo['response']}")
                    st.markdown("---")


# Main App Logic
placeholder = st.empty()
if st.session_state.logged_in:
    chatbot_ui(placeholder)
else:
    login_ui(placeholder)
