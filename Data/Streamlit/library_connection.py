from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import streamlit as st

def connect_to_db(password):
    """
    Attempts to connect to the DB with the MySQL password.
    Returns (engine, None) on success.
    Returns (None, error_message) on failure.
    """
    schema = "Lianes_Library"
    host = "127.0.0.1"
    user = "root"
    port = 3306

    try:
        connection_string = f'mysql+pymysql://{user}:{password}@{host}:{port}/{schema}'
        engine = create_engine(connection_string, pool_pre_ping=True, connect_args={'connect_timeout': 5})
        
        # Test connection
        connection = engine.connect()
        connection.close()
        
        return engine, None  # Return the engine and no error (tuple unpacking)

    except SQLAlchemyError as e:
        error_message = "Connection failed: The password you entered is incorrect or the database is unavailable."
        return None, error_message # Return no engine and the error message (tuple unpacking)

def disconnect_db():
    """Disconnects the engine and resets the state."""
    if st.session_state.get("engine"):
        st.session_state.engine.dispose()
    st.session_state.engine = None
    st.session_state.db_status = "Disconnected"
    st.switch_page("Login.py")