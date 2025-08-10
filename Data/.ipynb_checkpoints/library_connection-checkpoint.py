# library_connection.py
import os
import streamlit as st
from sqlalchemy import create_engine

def get_engine():
    if "engine" not in st.session_state or st.session_state.engine is None:
        DB_PATH = os.path.join(os.path.dirname(__file__), "library.db")
        st.session_state.engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
    return st.session_state.engine