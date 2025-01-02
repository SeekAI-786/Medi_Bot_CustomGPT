# Check if the user is logged in
if not st.session_state.logged_in:
    # Show Login/Register interface
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.header("Medi Bot 🤖")
    st.subheader("Login/Register")

    auth_action = st.radio("Select Action", ["Login", "Register", "Guest Login"], horizontal=True)

    if auth_action == "Register":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Register"):
            register_user(email, password, confirm_password)

    if auth_action == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(email, password):  # Redirects to chatbot if login succeeds
                st.experimental_rerun()

    if auth_action == "Guest Login":
        if st.button("Enter as Guest"):
            st.session_state.logged_in = True
            st.session_state.user_email = "Guest"
            st.experimental_rerun()  # Refresh to load chatbot interface

    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Show Chatbot interface
    st.sidebar.success(f"Logged in as {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.conversations = []
        st.experimental_rerun()  # Refresh to load login interface

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

    if clear_button:
        st.session_state.conversations = []
        st.success("Conversation history cleared.")

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

    if st.session_state.conversations:
        st.subheader("📝 Conversation History")
        for convo in st.session_state.conversations:
            st.markdown('<div class="chat-response">', unsafe_allow_html=True)
            st.write(f"**You:** {convo['query']}")
            st.write(f"**Medi Bot:** {convo['response']}")
            st.markdown('<hr>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
