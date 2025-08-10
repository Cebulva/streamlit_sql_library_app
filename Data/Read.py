import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import datetime, timedelta

def list_books():
    """
    Retrieves all books from the database using the shared engine
    from the session state.
    """
    if "engine" not in st.session_state or st.session_state.engine is None:
        st.error("Database connection not found.")
        return pd.DataFrame()
    engine = st.session_state.engine
    return pd.read_sql("SELECT * FROM Books", engine)

def list_loans():
    """
    Retrieves all active loans from the database using the shared engine
    from the session state.
    """
    if "engine" not in st.session_state or st.session_state.engine is None:
        st.error("Database connection not found.")
        return pd.DataFrame()
    engine = st.session_state.engine
    query = """
            SELECT LoanID, FriendID, FName, LName, BorrowDate, DueDate, ReturnReminder, Title, Loans.ISBN
            FROM Loans
            JOIN Books USING (ISBN)
            JOIN Friends USING (FriendID)
            """
    return pd.read_sql(query, engine)

def loan_exists(LoanID):
    if "engine" not in st.session_state or st.session_state.engine is None:
        return False
    engine = st.session_state.engine
    query = text("SELECT 1 FROM Loans WHERE LoanID = :LoanID LIMIT 1")
    with engine.connect() as conn:
        result = conn.execute(query, {"LoanID": LoanID}).fetchone()
        return result is not None

def book_exists(isbn):
    if "engine" not in st.session_state or st.session_state.engine is None:
        return False # Return a boolean for consistency
    engine = st.session_state.engine
    query = text("SELECT 1 FROM Books WHERE ISBN = :isbn LIMIT 1")
    with engine.connect() as conn:
        return conn.execute(query, {"isbn": isbn}).fetchone() is not None

def read_all_books():
    if "engine" not in st.session_state or st.session_state.engine is None:
        return pd.DataFrame()
    engine = st.session_state.engine
    return pd.read_sql("SELECT * FROM Books ORDER BY Title", engine)

def read_books():
    if "engine" not in st.session_state or st.session_state.engine is None:
        return pd.DataFrame()
    engine = st.session_state.engine

    query = """
        SELECT 
            ISBN, 
            Title, 
            Author, 
            Genre, 
            IsInStock, 
            BookCondition as 'Condition', 
            ShelfLocation || ' ' || ShelfRow as Location 
        FROM Books 
        ORDER BY Title
    """
    return pd.read_sql(query, engine)

def count_books():
    if "engine" not in st.session_state or st.session_state.engine is None:
        return 0 # Return a number for consistency
    engine = st.session_state.engine
    return pd.read_sql("SELECT COUNT(*) AS count FROM Books", engine)["count"][0]

def count_borrowed_books():
    if "engine" not in st.session_state or st.session_state.engine is None:
        return 0 # Return a number for consistency
    engine = st.session_state.engine
    return pd.read_sql("SELECT COUNT(*) AS count FROM Loans", engine)["count"][0]

def count_overdue_books():
    if "engine" not in st.session_state or st.session_state.engine is None:
        return 0 # Return a number for consistency
    engine = st.session_state.engine
    # ✅ Replaced MySQL's CURRENT_DATE with SQLite's date('now')
    return pd.read_sql("SELECT COUNT(*) AS count FROM Loans WHERE DueDate < date('now')", engine)["count"][0]

def get_friends():
    """Fetches all friends from the database for dropdowns."""
    if "engine" not in st.session_state or st.session_state.engine is None:
        return pd.DataFrame()
    engine = st.session_state.engine
    query = text("SELECT FriendID, FName, LName, MaxLoans FROM Friends ORDER BY FName, LName")
    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
            df['display'] = df['FName'] + ' ' + df['LName'] + ' (ID: ' + df['FriendID'].astype(str) + ')'
            return df
    except Exception as e:
        st.error(f"Error fetching friends: {e}")
        return pd.DataFrame()

def get_books():
    """Fetches available books from the database for dropdowns."""
    if "engine" not in st.session_state or st.session_state.engine is None:
        return pd.DataFrame()
    engine = st.session_state.engine
    query = text("SELECT ISBN, Title FROM Books WHERE IsInStock = 1 ORDER BY Title")
    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
            df['display'] = df['Title'] + ' (ISBN: ' + df['ISBN'] + ')'
            return df
    except Exception as e:
        st.error(f"Error fetching available books: {e}")
        return pd.DataFrame()

def get_borrowed_books(friend_id):
    """Fetches books borrowed by a specific friend."""
    if not friend_id or "engine" not in st.session_state or st.session_state.engine is None:
        return pd.DataFrame()
    engine = st.session_state.engine
    query = text("""
        SELECT B.ISBN, B.Title FROM Loans L JOIN Books B ON L.ISBN = B.ISBN
        WHERE L.FriendID = :friend_id ORDER BY B.Title
    """)
    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, connection, params={"friend_id": friend_id})
            df['display'] = df['Title'] + ' (ISBN: ' + df['ISBN'] + ')'
            return df
    except Exception as e:
        st.error(f"Error fetching borrowed books: {e}")
        return pd.DataFrame()

def get_loan_friends():
    """Fetches unique friends who currently have loans."""
    if "engine" not in st.session_state or st.session_state.engine is None:
        return pd.DataFrame()
    engine = st.session_state.engine
    query = text("SELECT DISTINCT FriendID, FName, LName FROM Loans JOIN Friends USING (FriendID) ORDER BY FName, LName")
    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
            df['display'] = df['FName'] + ' ' + df['LName'] + ' (ID: ' + df['FriendID'].astype(str) + ')'
            return df
    except Exception as e:
        st.error(f"Error fetching friends with loans: {e}")
        return pd.DataFrame()
        
def get_loan_overdues():
    """Fetches loans which are overdue."""
    if "engine" not in st.session_state or st.session_state.engine is None:
        return pd.DataFrame()
    engine = st.session_state.engine
    # ✅ Replaced MySQL's Now() with SQLite's datetime('now') and removed the JOIN to Contacts
    query = text("""
            SELECT LoanID, DueDate, FriendID, FName, LName, Title, Loans.ISBN 
            FROM Loans
            JOIN Books USING (ISBN)
            JOIN Friends USING (FriendID)
            WHERE DueDate < datetime('now')
            """)
    return pd.read_sql(query, engine)

def get_friend_contact_info(friend_id):
    """Fetches all contact details for a specific friend."""
    if not friend_id or "engine" not in st.session_state or st.session_state.engine is None:
        return pd.DataFrame()
    engine = st.session_state.engine
    query = text("SELECT ContactID, type, contact FROM Contacts WHERE FriendID = :friend_id")
    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, connection, params={"friend_id": friend_id})
            return df
    except Exception as e:
        st.error(f"Error fetching contact info: {e}")
        return pd.DataFrame()

def get_friend_max_loans(friend_id):
    """Fetches the MaxLoans value for a single friend."""
    if not friend_id or "engine" not in st.session_state or st.session_state.engine is None:
        return None
    engine = st.session_state.engine
    query = text("SELECT MaxLoans FROM Friends WHERE FriendID = :friend_id")
    try:
        with engine.connect() as connection:
            result = pd.read_sql(query, connection, params={"friend_id": friend_id})
            if not result.empty:
                return result["MaxLoans"].iloc[0]
            return None
    except Exception:
        return None

def get_daily_reminders():
    """Fetches loans with a reminder date of today."""
    if "engine" not in st.session_state or st.session_state.engine is None:
        return pd.DataFrame()
    engine = st.session_state.engine
    # ✅ Replaced MySQL's CURDATE() with SQLite's date('now')
    query = text("""
        SELECT 
            L.LoanID, L.DueDate, 
            F.FriendID, F.FName, F.LName, 
            B.Title,
            C.type, C.contact
        FROM Loans L
        JOIN Friends F ON L.FriendID = F.FriendID
        JOIN Books B ON L.ISBN = B.ISBN
        JOIN Contacts C ON L.FriendID = C.FriendID
        WHERE date(L.ReturnReminder) = date('now')
    """)
    try:
        with engine.connect() as connection:
            return pd.read_sql(query, connection)
    except Exception as e:
        st.error(f"Error fetching reminders: {e}")
        return pd.DataFrame()