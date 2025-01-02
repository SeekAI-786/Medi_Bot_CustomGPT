# Imports
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
from huggingface_hub import InferenceClient

# Load Firebase credentials and Hugging Face API key from Streamlit secrets
firebase_config = dict(st.secrets["firebase"])  # Converts secrets into a dictionary
hf_api_key = st.secrets["api"]["huggingface_api_key"]

# Initialize Streamlit session state keys
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "conversations" not in st.session_state:
    st.session_state.conversations = []  # Clear conversations for new user login

# Initialize Firebase if not already done
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

# CSS styling for professional UI
st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #ffffff; 
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Firebase Authentication Functions
def register_user(email, password, confirm_password):
    if password != confirm_password:
        st.error("Passwords do not match!")
        return
    try:
        user = auth.create_user(email=email, password=password)
        st.success("User registered successfully! You can now log in.")
    except Exception as e:
        st.error(f"Registration error: {e}")

def login_user(email, password):
    try:
        user_ref = db.collection("users").where("email", "==", email).stream()
        if any(user_ref):  # Check if user exists
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.session_state.conversations = []  # Clear conversations for new login
            st.success(f"Welcome back, {email}!")
            return True
        else:
            st.error("Invalid credentials or user does not exist.")
            return False
    except Exception as e:
        st.error(f"Login error: {e}")

# Ensure there is no content or layout before components
st.empty()  # Clear any implicit Streamlit placeholders

# Login/Register Interface
if not st.session_state.logged_in:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.header("Medi Bot 🤖")
    st.subheader("Login/Register")

    auth_action = st.radio("Select Action", ["Login", "Register"], horizontal=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if auth_action == "Register":
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Register"):
            register_user(email, password, confirm_password)

    if auth_action == "Login":
        if st.button("Login"):
            login_successful = login_user(email, password)
            if login_successful:
                st.session_state.logged_in = True

    st.markdown('</div>', unsafe_allow_html=True)

# Chatbot Interface
if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.conversations = []

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.header("Medi Bot 🤖💬")
    st.caption("Your personalized medical assistant.")

    available_models = [
        "gemma-mental-health-fine-tune",
        "Mistral-1.5B-medical-QA",
        "llama-3.2-1B-Lora-Fine_Tune-FineTome",
    ]
    selected_model = st.selectbox("Choose a model:", available_models)

    user_query = st.text_input("Your message:", placeholder="Type your query here...")
    col1, col2 = st.columns(2)
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
            response = None
            friendly_instruction = (
                "You are a helpful and friendly medical assistant. Please refrain from giving personal, offensive, "
                "or abusive answers. Be respectful and professional in your responses."
            )
            query = friendly_instruction + user_query

            try:
                client = InferenceClient(api_key=hf_api_key)
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
                    model=model_name, messages=messages, max_tokens=700
                )
                response = completion.choices[0].message.content
            except Exception as e:
                st.error(f"Hugging Face API error: {e}")

            if response:
                st.session_state.conversations.append({"query": user_query, "response": response})

    # Display Chat History with Separators
    if st.session_state.conversations:
        st.subheader("📝 Conversation History")
        for convo in st.session_state.conversations:
            st.markdown('<div class="chat-response">', unsafe_allow_html=True)
            st.write(f"**You:** {convo['query']}")
            st.write(f"**Medi Bot:** {convo['response']}")
            st.markdown('<hr>', unsafe_allow_html=True)  # Separator between messages
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
