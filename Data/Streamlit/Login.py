import streamlit as st
import library_connection

# --- Page Configuration ---
st.set_page_config(page_title="Library Connection", page_icon="📚")

# --- Session State Initialization ---
if "db_status" not in st.session_state:
    st.session_state.db_status = "Disconnected"
if "engine" not in st.session_state:
    st.session_state.engine = None

# --- Main App Logic ---
st.title("Database Connection Manager")

if st.session_state.db_status == "Connected":
    st.switch_page("pages/02_Home.py")

# --- Login Form ---
st.info("Please enter your MySQL password to continue.")
with st.form("db_login_form", clear_on_submit=True):
    password_input = st.text_input("MySQL Password", type="password")
    
    submitted = st.form_submit_button("Connect")
    if submitted:
        engine, error = library_connection.connect_to_db(password_input)

        if engine:
            st.session_state.engine = engine
            st.session_state.db_status = "Connected"
            st.switch_page("pages/02_Home.py")
        else:
            st.error(error)
            