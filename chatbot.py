import streamlit as st

# Streamlit session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# CSS Styling for the dark-themed UI
st.markdown(
    """
    <style>
    body {
        background-color: #121212;
        color: #ffffff;
        font-family: Arial, sans-serif;
    }
    
    </style>
    """,
    unsafe_allow_html=True,
)

# Display tab-based layout
tabs = ["Create new account", "Login to existing account", "Guest login"]
selected_tab = st.radio("", tabs, horizontal=True)

st.markdown('<div class="login-box">', unsafe_allow_html=True)

# Content for each tab
if selected_tab == "Create new account":
    st.subheader("Create a New Account")
    username = st.text_input("Enter your unique username")
    password = st.text_input("Enter your password", type="password")
    confirm_password = st.text_input("Confirm your password", type="password")
    if st.button("Register"):
        if password != confirm_password:
            st.markdown('<div class="error-message">Passwords do not match!</div>', unsafe_allow_html=True)
        else:
            # Simulate account creation (replace with actual backend logic)
            st.markdown('<div class="success-message">Account created successfully! 🎉</div>', unsafe_allow_html=True)

elif selected_tab == "Login to existing account":
    st.subheader("Login to Your Account")
    username = st.text_input("Enter your unique username", key="login_username")
    password = st.text_input("Enter your password", type="password", key="login_password")
    if st.button("Login"):
        # Simulate login (replace with actual authentication logic)
        if username == "JohnDoe" and password == "12345":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.markdown('<div class="success-message">Login succeeded 🎉</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-message">Invalid username or password!</div>', unsafe_allow_html=True)

elif selected_tab == "Guest login":
    st.subheader("Continue as a Guest")
    if st.button("Enter as Guest"):
        st.session_state.logged_in = True
        st.session_state.username = "Guest"
        st.markdown('<div class="success-message">Logged in as Guest 🎉</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Display logout button if logged in
if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Logged out successfully.", icon="✅")
