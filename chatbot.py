import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
from huggingface_hub import InferenceClient

# Load Firebase credentials and Hugging Face API key from Streamlit secrets
firebase_config = dict(st.secrets["firebase"])  # Converts secrets into a dictionary
hf_api_key = st.secrets["api"]["huggingface_api_key"]

# Initialize Firebase if not already done
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()  # Firestore for user information

# CSS styling for professional UI
st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f4f4f9;
    }
    .centered-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        background-color: #007bff;
    }
    .login-box {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        text-align: center;
        width: 100%;
        max-width: 400px;
    }
    .chat-container {
        margin: 2rem auto;
        max-width: 800px;
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }
    .chat-response {
        background: #f9f9f9;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
    }
    button {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    button:hover {
        background-color: #0056b3;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session state for user authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

# Firebase Authentication Functions
def register_user(email, password, confirm_password):
    if password != confirm_password:
        st.error("Passwords do not match!")
        return
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({"email": email})
        st.success("User registered successfully! You can now log in.")
    except Exception as e:
        st.error(f"Registration error: {e}")

def login_user(email, password):
    try:
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

# Login/Register Interface
if not st.session_state.logged_in:
    st.markdown('<div class="centered-container">', unsafe_allow_html=True)
    with st.container():
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
                if login_user(email, password):
                    st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Chatbot Interface
if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.experimental_rerun()

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.header("Medi Bot 🤖💬")
    st.caption("Your personalized medical assistant.")

    available_models = [
        "gemma-mental-health-fine-tune",
        "qwen-1.5B-medical-QA",
        "llama-3.2-1B-Lora-Fine_Tune-FineTome",
    ]
    selected_model = st.selectbox("Choose a model:", available_models)

    user_query = st.text_input("Your message:", placeholder="Type your query here...")
    generate_button = st.button("Generate Response")
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

            if response:
                if "conversations" not in st.session_state:
                    st.session_state.conversations = []
                st.session_state.conversations.append({"query": user_query, "response": response})
                st.experimental_rerun()

    # Display Chat History
    if "conversations" in st.session_state:
        st.subheader("📝 Conversation History")
        for convo in st.session_state.conversations:
            st.markdown('<div class="chat-response">', unsafe_allow_html=True)
            st.write(f"**You:** {convo['query']}")
            st.write(f"**Medi Bot:** {convo['response']}")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
