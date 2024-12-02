import streamlit as st
from huggingface_hub import InferenceClient
import requests
import json

# Initialize the Hugging Face Inference Client
hf_api_key = "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"  # Replace with your actual Hugging Face API key
client = InferenceClient(api_key=hf_api_key)

# Gemini API Key
gemini_api_key = "AIzaSyBODZWYE_MUpwUBzJUhPKr9Wrk_47yiFO4"  # Replace with your actual Gemini API key
gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# List of available models for selection
available_models = [
    "meta-llama/Llama-3.2-1B-Instruct",
    "Qwen/Qwen2.5-72B-Instruct",
    "google/gemma-1.1-2b-it",
    "microsoft/Phi-3.5-mini-instruct",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "01-ai/Yi-1.5-34B-Chat",
    "Gemini Model"  # Gemini added as a new option
]

# Initialize session state to store conversation
if "conversations" not in st.session_state:
    st.session_state.conversations = []
    st.session_state.is_generating = False  # To track response generation state

# Streamlit app layout
st.set_page_config(
    page_title="AI Chat Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 AI Chat Interface")
st.markdown("""
    <style>
        .stTitle {color: #3A3A3A; font-size: 2.5rem; text-align: center;}
        .stSubtitle {color: #3A3A3A; font-size: 1.25rem; margin-bottom: 10px;}
        .stButton button {background-color: #4CAF50; color: white;}
        .response-box {background-color: #f4f4f4; padding: 15px; border-radius: 5px;}
        .conversation-container {background-color: #e9ecef; padding: 15px; border-radius: 10px; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.subheader("Select a model and interact with it!")

# Sidebar for model selection and actions
with st.sidebar:
    st.markdown("## Model Selection")
    selected_model = st.selectbox("Choose a model:", options=available_models)
    st.markdown("## Actions")
    if st.button("Clear All Conversations", key="sidebar_clear"):
        st.session_state.conversations = []
        st.session_state.is_generating = False  # Reset the generating flag
        st.success("All conversations cleared.")

# Main area for input and results
st.write("---")
col_input, col_output = st.columns([1, 2])

with col_input:
    st.markdown("### Enter your query")
    user_query = st.text_area("Your query:", placeholder="Type your question or prompt here...", height=150)
    if st.button("Generate Response"):
        if not user_query.strip():
            st.warning("Please enter a query.")
        elif st.session_state.is_generating:
            st.warning("Response is already being generated. Please wait.")
        else:
            st.session_state.is_generating = True  # Set flag to true to indicate generation in progress
            
            response = None  # Initialize the response variable
            if selected_model == "Gemini Model":
                # Gemini API Request
                payload = {
                    "contents": [{"parts": [{"text": user_query}]}]
                }
                headers = {"Content-Type": "application/json"}
                
                try:
                    gemini_response = requests.post(
                        f"{gemini_url}?key={gemini_api_key}",
                        headers=headers,
                        data=json.dumps(payload)
                    )
                    gemini_response.raise_for_status()
                    response_data = gemini_response.json()
                    if "candidates" in response_data and response_data["candidates"]:
                        generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                        response = generated_text
                    else:
                        st.error("No content found in the response.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred with the Gemini Model: {e}")
            else:
                # Handle Hugging Face models
                try:
                    messages = [{"role": "user", "content": user_query}]
                    with st.spinner(f"Generating response using {selected_model}..."):
                        completion = client.chat.completions.create(
                            model=selected_model,
                            messages=messages,
                            max_tokens=700
                        )
                        response = completion.choices[0].message.content
                except Exception as e:
                    st.error(f"An error occurred with model {selected_model}: {e}")

            if response:
                st.session_state.conversations.append({"query": user_query, "response": response})
            st.session_state.is_generating = False  # Reset flag

with col_output:
    st.markdown("### Conversation History")
    if st.session_state.conversations:
        for idx, convo in enumerate(st.session_state.conversations):
            with st.expander(f"Conversation {idx + 1}"):
                st.markdown(f"**Prompt:** {convo['query']}")
                st.markdown(f"**Response:**")
                st.markdown(f"<div class='response-box'>{convo['response']}</div>", unsafe_allow_html=True)
    else:
        st.info("No conversations yet. Your responses will appear here.")

