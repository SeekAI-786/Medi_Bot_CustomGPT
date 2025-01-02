# Imports
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
from huggingface_hub import InferenceClient

# Firebase Initialization
firebase_config = dict(st.secrets["firebase"])
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

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
def login_ui(placeholder):
    with placeholder.container():
        st.header("Welcome to Medi Bot 🤖")
        action = st.radio("Select Action", ["Login", "Register", "Guest Login"], horizontal=True)

        if action == "Register":
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            if st.button("Register"):
                if password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    try:
                        auth.create_user(email=email, password=password)
                        st.success("Registration successful! Please log in.")
                    except Exception as e:
                        st.error(f"Error: {e}")

        elif action == "Login":
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                try:
                    user_ref = db.collection("users").where("email", "==", email).stream()
                    if any(user_ref):
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.session_state.conversations = []
                        st.success(f"Welcome, {email}!")
                        placeholder.empty()
                        chatbot_ui(placeholder)
                    else:
                        st.error("Invalid credentials or user does not exist.")
                except Exception as e:
                    st.error(f"Error: {e}")

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
        available_models = ["gemma-mental-health-fine-tune", "Mistral-1.5B-medical-QA"]
        selected_model = st.selectbox("Choose a model:", available_models)

        chat_container = st.empty()
        with st.container():
            user_input = st.text_input("Your message:", placeholder="Type here...")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Send"):
                    if user_input.strip():
                        st.session_state.conversations.append({"query": user_input, "response": "Mock response"})
                        user_input = ""
            with col2:
                if st.button("Clear"):
                    st.session_state.conversations = []

        with chat_container.container():
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
