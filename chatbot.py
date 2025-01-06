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
if "user_input" not in st.session_state:
    st.session_state.user_input = ""  # Initialize user input in session state.

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
            st.session_state.user_input = ""  # Reset input on logout
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
            # Use st.text_input without the key binding and rely on session state to store user input
            user_input = st.text_input("Your message:", placeholder="Type your query here...")
            st.session_state.user_input = user_input  # Store the value in session state
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("Generate Response"):
                    if st.session_state.user_input.strip():
                        try:
                            response = None
                            friendly_instruction = (
                                "You are a helpful and friendly medical assistant. Please refrain from giving personal, offensive, "
                                "or abusive answers. Be respectful and professional in your responses."
                            )
                            query = friendly_instruction + st.session_state.user_input

                            client = InferenceClient(api_key=st.secrets["api"]["huggingface_api_key"])
                            messages = [{"role": "user", "content": query}]

                            if selected_model == "llama-3.2-1B-Lora-Fine_Tune-FineTome":
                                model_name = "unsloth/Llama-3.2-1B-Instruct"
                                messages = [{"role": "system", "content": "Medical information bot"}] + messages
                            elif selected_model == "Mistral-1.5B-medical-QA":
                                model_name = "mistralai/Mixtral-8x7B-Instruct-v0.1"
                                messages = [{"role": "system", "content": friendly_instruction}] + messages
                            elif selected_model == "gemma-mental-health-fine-tune":
                                model_name = "google/gemma-1.1-2b-it"

                            completion = client.chat.completions.create(
                                model=model_name, messages=messages, max_tokens=1000
                            )
                            response = completion.choices[0].message.content

                            if response:
                                st.session_state.conversations.append({"query": st.session_state.user_input, "response": response})

                            # Reset the input field after sending
                            st.session_state.user_input = ""

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
                st.subheader("📝 Conversation History")
                for convo in st.session_state.conversations:
                    st.markdown(f"You: {convo['query']}")
                    st.markdown(f"Medi Bot: {convo['response']}")
                    st.markdown("---")

# Main App Logic
placeholder = st.empty()
if st.session_state.logged_in:
    chatbot_ui(placeholder)
else:
    login_ui(placeholder)
