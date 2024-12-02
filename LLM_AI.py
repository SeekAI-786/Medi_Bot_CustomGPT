import streamlit as st
from huggingface_hub import InferenceClient
import requests
import json
import pdfplumber  # For extracting text from PDFs

# Initialize session state for storing API keys, conversations, and PDF content
if "hf_api_key" not in st.session_state:
    st.session_state.hf_api_key = ""
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""
if "conversations" not in st.session_state:
    st.session_state.conversations = []
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""

# App Title and Layout
st.title("EcoQuery 🌍💬")

st.caption("Your go-to chatbot for insightful conversations on the environment, nature, and sustainability 🌿♻️")


# Sidebar for API key input
st.sidebar.header("API Configuration")
st.sidebar.subheader("Enter your API keys:")
st.session_state.hf_api_key = st.sidebar.text_input(
    "Hugging Face API Key",
    value=st.session_state.hf_api_key,
    type="password",
    placeholder="Enter Hugging Face API key"
)
st.session_state.gemini_api_key = st.sidebar.text_input(
    "Gemini API Key",
    value=st.session_state.gemini_api_key,
    type="password",
    placeholder="Enter Gemini API key"
)

# Model Selection
st.sidebar.subheader("Model Selection")
available_models = [
    "meta-llama/Llama-3.2-1B-Instruct",
    "Qwen/Qwen2.5-72B-Instruct",
    "google/gemma-1.1-2b-it",
    "microsoft/Phi-3.5-mini-instruct",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "01-ai/Yi-1.5-34B-Chat",
    "Gemini Model"
]
selected_model = st.sidebar.selectbox("Choose a model:", available_models)

# PDF Upload Section (Only for Gemini Model)
if selected_model == "Gemini Model":
    st.sidebar.subheader("📄 PDF Upload (Gemini Model)")
    uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type="pdf")

    if uploaded_file is not None:
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                pdf_text = ""
                for page in pdf.pages:
                    pdf_text += page.extract_text()
            st.session_state.pdf_content = pdf_text
            st.sidebar.success("PDF uploaded and processed successfully.")
        except Exception as e:
            st.sidebar.error(f"Failed to process PDF: {e}")

# User Input Section
st.subheader("💬 Chat with the Model")
user_query = st.text_input("Your message:", placeholder="Type your query here...")

# Buttons
col1, col2 = st.columns([1, 0.320])
with col1:
    generate_button = st.button("Generate Response")
with col2:
    clear_button = st.button("Clear Conversations")

# Handle Clear Button
if clear_button:
    st.session_state.conversations = []
    st.session_state.pdf_content = ""
    st.success("Conversation history and PDF content cleared.")

# Handle Generate Button
if generate_button:
    if not user_query.strip():
        st.warning("Please enter a message.")
    elif not st.session_state.hf_api_key and selected_model != "Gemini Model":
        st.warning("Please enter your Hugging Face API key.")
    elif not st.session_state.gemini_api_key and selected_model == "Gemini Model":
        st.warning("Please enter your Gemini API key.")
    else:
        # Generate Response
        response = None
        if selected_model == "Gemini Model":
            # Prepare the query for Gemini
            if st.session_state.pdf_content:
                # Combine PDF content with user query
                combined_query = f"Based on the following PDF content:\n\n{st.session_state.pdf_content}\n\nQuestion: {user_query}"
            else:
                # Use only the user query
                combined_query = user_query

            payload = {"contents": [{"parts": [{"text": combined_query}]}]}
            headers = {"Content-Type": "application/json"}
            gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            try:
                gemini_response = requests.post(
                    f"{gemini_url}?key={st.session_state.gemini_api_key}",
                    headers=headers,
                    data=json.dumps(payload)
                )
                gemini_response.raise_for_status()
                response_data = gemini_response.json()
                if "candidates" in response_data:
                    response = response_data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                st.error(f"Gemini API error: {e}")
        else:
            # Hugging Face API
            try:
                client = InferenceClient(api_key=st.session_state.hf_api_key)
                messages = [{"role": "user", "content": user_query}]
                completion = client.chat.completions.create(
                    model=selected_model, messages=messages, max_tokens=700
                )
                response = completion.choices[0].message.content
            except Exception as e:
                st.error(f"Hugging Face API error: {e}")

        # Update Conversation History
        if response:
            st.session_state.conversations.append({"query": user_query, "response": response})
            st.success("Response generated!")

# Display Conversation History
if st.session_state.conversations:
    st.subheader("📝 Conversation History")
    # Reverse the list so that the latest conversation is shown at the top
    for idx, convo in enumerate(reversed(st.session_state.conversations)):
        st.write(f"**Prompt {len(st.session_state.conversations) - idx}:** {convo['query']}")
        st.write(f"**Response {len(st.session_state.conversations) - idx}:** {convo['response']}")

