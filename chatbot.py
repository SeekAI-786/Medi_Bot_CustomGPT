import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
from huggingface_hub import InferenceClient

# Load Firebase credentials from Streamlit secrets
firebase_config = dict(st.secrets["firebase"])  # This converts the secrets into a dictionary format

# Initialize Firebase if not already done
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)  # Pass the dictionary as credentials
    firebase_admin.initialize_app(cred)



db = firestore.client()  # Firestore for user information

# Session state for user authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

# App Title and Layout
st.title("Medi Bot 🤖💬")
st.caption("Your personalized medical assistant. Created by Qusai Jamali (22108131) and Muhammad (22108137)")

# Firebase Authentication Functions
def register_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({"email": email})
        st.success("User registered successfully!")
    except Exception as e:
        st.error(f"Registration error: {e}")

def login_user(email, password):
    try:
        # Authenticate user using Firestore for simplicity (use Firebase Auth for more secure handling)
        user_ref = db.collection("users").where("email", "==", email).stream()
        if any(user_ref):  # Check if user exists
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success(f"Welcome back, {email}!")
            return True
        else:
            st.error("Invalid credentials or user does not exist.")
            return False
    except Exception as e:
        st.error(f"Login error: {e}")

# User Authentication System
if not st.session_state.logged_in:
    st.sidebar.header("Login/Register")

    auth_action = st.sidebar.radio("Select Action", ["Login", "Register"])
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if auth_action == "Register" and st.sidebar.button("Register"):
        if email and password:
            register_user(email, password)
        else:
            st.sidebar.warning("Please provide both email and password.")

    if auth_action == "Login" and st.sidebar.button("Login"):
        if email and password:
            login_user(email, password)
        else:
            st.sidebar.warning("Please provide both email and password.")
else:
    st.sidebar.success(f"Logged in as {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""

# Main App (Only Accessible after Login)
if st.session_state.logged_in:
    st.sidebar.subheader("Model Selection")
    available_models = [
        "gemma-mental-health-fine-tune",
        "qwen-1.5B-medical-QA",
        "llama-3.2-1B-Lora-Fine_Tune-FineTome"
    ]
    selected_model = st.sidebar.selectbox("Choose a model:", available_models)

    st.subheader("💬 Chat with the Medi Bot")
    user_query = st.text_input("Your message:", placeholder="Type your query here...")

    # Buttons for response generation and clearing
    col1, col2 = st.columns([1, 0.320])
    with col1:
        generate_button = st.button("Generate Response")
    with col2:
        clear_button = st.button("Clear Conversation History")

    # Handle Clear Button
    if clear_button:
        st.session_state.conversations = []
        st.success("Conversation history cleared.")

    # Handle Generate Button
    if generate_button:
        if not user_query.strip():
            st.warning("Please enter a message.")
        else:
            # Generate Response based on model selection
            response = None

            friendly_instruction = (
                "You are a helpful and friendly medical assistant. Please refrain from giving personal, offensive, "
                "or abusive answers. Be respectful and professional in your responses."
            )
            query = friendly_instruction + user_query

            try:
                client = InferenceClient(api_key=api_key)
                messages = [{"role": "user", "content": query}]

                if selected_model == "llama-3.2-1B-Lora-Fine_Tune-FineTome":
                    model_name = "unsloth/Llama-3.2-1B-Instruct"
                    messages = [{"role": "system", "content": "Medical information bot"}] + messages
                
                elif selected_model == "qwen-1.5B-medical-QA":
                    model_name = "Qwen/Qwen2.5-1.5B-Instruct"
                    messages = [{"role": "system", "content": friendly_instruction}] + messages
                
                elif selected_model == "gemma-mental-health-fine-tune":
                    model_name = "google/gemma-1.1-2b-it"

                completion = client.chat.completions.create(
                    model=model_name, messages=messages, max_tokens=700
                )
                response = completion.choices[0].message.content
            except Exception as e:
                st.error(f"Hugging Face API error: {e}")

            # Display the response
            if response:
                if "conversations" not in st.session_state:
                    st.session_state.conversations = []
                st.session_state.conversations.append({"query": user_query, "response": response})
                st.success("Response generated!")
                st.write(f"**Response:** {response}")

    # Display previous conversation history
    if "conversations" in st.session_state:
        st.subheader("📝 Previous Conversations")
        for idx, convo in enumerate(reversed(st.session_state.conversations)):
            st.write(f"**Prompt {len(st.session_state.conversations) - idx}:** {convo['query']}")
            st.write(f"**Response {len(st.session_state.conversations) - idx}:** {convo['response']}")
