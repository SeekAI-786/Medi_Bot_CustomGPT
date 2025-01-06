import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
from huggingface_hub import InferenceClient
import requests
import pdfplumber
import json

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
if "gemini_pdf_content" not in st.session_state:
    st.session_state.gemini_pdf_content = ""

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
        auth.create_user(email=email, password=password)
        st.success("Registration successful! Please log in.")
    except Exception as e:
        st.error(f"Error: {e}")

def login_user(email, password, placeholder):
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
            st.session_state.gemini_pdf_content = ""
            placeholder.empty()
            login_ui(placeholder)

        st.header("Medi Bot 🤖")
        st.caption("Your personalized medical assistant.")

        available_models = [
            "gemma-mental-health-fine-tune",
            "Mistral-1.5B-medical-QA",
            "llama-3.2-1B-Lora-Fine_Tune-FineTome",
            "Gemini Model",
        ]
        selected_model = st.selectbox("Choose a model:", available_models)

        # Gemini-specific PDF Upload
        if selected_model == "Gemini Model":
            st.subheader("📄 Upload PDF for Gemini Model")
            gemini_pdf_uploaded = st.file_uploader("Upload a PDF for Context", type=["pdf"])
            if gemini_pdf_uploaded:
                try:
                    with pdfplumber.open(gemini_pdf_uploaded) as pdf:
                        pdf_text = ''.join(page.extract_text() for page in pdf.pages)
                        st.session_state.gemini_pdf_content = pdf_text
                        st.success("PDF successfully processed.")
                except Exception as e:
                    st.error(f"PDF Processing Error: {e}")

        # Chat Interaction
        user_input = st.text_input("Your message:", placeholder="Type your query here...", key="user_input")

        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Generate Response"):
                if user_input.strip():
                    try:
                        response = None
                        if selected_model == "Gemini Model":
                            gemini_api_key = st.secrets["api"].get("gemini_api_key")
                            if gemini_api_key:
                                gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

                                combined_query = (
                                    f"Context from PDF:\n\n{st.session_state.gemini_pdf_content}\n\nUser Query:\n{user_input}"
                                    if st.session_state.gemini_pdf_content else user_input
                                )
                                payload = {"contents": [{"parts": [{"text": combined_query}]}]}
                                headers = {"Content-Type": "application/json"}

                                gemini_response = requests.post(
                                    f"{gemini_url}?key={gemini_api_key}",
                                    headers=headers,
                                    data=json.dumps(payload),
                                )
                                gemini_response.raise_for_status()
                                response_data = gemini_response.json()
                                response = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

                        else:
                            # Handle other models with Hugging Face
                            friendly_instruction = "You are a friendly medical assistant."
                            query = f"{friendly_instruction}\n\n{user_input}"

                            client = InferenceClient(api_key=st.secrets["api"]["huggingface_api_key"])
                            messages = [{"role": "user", "content": query}]
                            completion = client.chat.completions.create(
                                model=selected_model,
                                messages=messages,
                                max_tokens=700,
                            )
                            response = completion.choices[0].message.content

                        if response:
                            st.session_state.conversations.append({"query": user_input, "response": response})
                            st.success("Response generated!")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please enter a message.")
        with col2:
            if st.button("Clear Conversation History"):
                st.session_state.conversations = []
                st.success("Conversation history cleared.")

        # Display Conversation History
        if st.session_state.conversations:
            st.subheader("📝 Conversation History")
        for convo in reversed(st.session_state.conversations):
        st.markdown(f"You: {convo['query']}")
        st.markdown(f"Medi Bot: {convo['response']}")
        st.markdown("---")


# Main App Logic
placeholder = st.empty()
if st.session_state.logged_in:
    chatbot_ui(placeholder)
else:
    login_ui(placeholder)
