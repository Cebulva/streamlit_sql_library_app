import streamlit as st
import pandas as pd
from sqlalchemy import text

def _get_engine():
    engine = st.session_state.get("engine")
    if engine is None:
        st.error("Database connection not found.")
    return engine

def list_books() -> pd.DataFrame:
    """Retrieve all books from the database."""
    engine = _get_engine()
    if not engine:
        return pd.DataFrame()
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM Books", conn)

def list_loans() -> pd.DataFrame:
    """Retrieve all active loans with friend and book details."""
    engine = _get_engine()
    if not engine:
        return pd.DataFrame()
    query = """
        SELECT LoanID, FriendID, FName, LName, BorrowDate, DueDate, ReturnReminder, Title, Loans.ISBN
        FROM Loans
        JOIN Books USING (ISBN)
        JOIN Friends USING (FriendID)
    """
    with engine.connect() as conn:
        return pd.read_sql(query, conn)

def loan_exists(LoanID: int) -> bool:
    """Check if a loan with LoanID exists."""
    engine = _get_engine()
    if not engine:
        return False
    query = text("SELECT 1 FROM Loans WHERE LoanID = :LoanID LIMIT 1")
    with engine.connect() as conn:
        return conn.execute(query, {"LoanID": LoanID}).fetchone() is not None

def book_exists(isbn: str) -> bool:
    """Check if a book with ISBN exists."""
    engine = _get_engine()
    if not engine:
        return False
    query = text("SELECT 1 FROM Books WHERE ISBN = :isbn LIMIT 1")
    with engine.connect() as conn:
        return conn.execute(query, {"isbn": isbn}).fetchone() is not None

def read_all_books() -> pd.DataFrame:
    """Read all books ordered by title."""
    engine = _get_engine()
    if not engine:
        return pd.DataFrame()
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM Books ORDER BY Title", conn)

def read_books() -> pd.DataFrame:
    """Read books with formatted location and condition."""
    engine = _get_engine()
    if not engine:
        return pd.DataFrame()
    query = """
        SELECT 
            ISBN, 
            Title, 
            Author, 
            Genre, 
            IsInStock, 
            BookCondition AS 'Condition', 
            ShelfLocation || ' ' || ShelfRow AS Location 
        FROM Books 
        ORDER BY Title
    """
    with engine.connect() as conn:
        return pd.read_sql(query, conn)

def count_books() -> int:
    """Count total books."""
    engine = _get_engine()
    if not engine:
        return 0
    query = "SELECT COUNT(*) AS count FROM Books"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
        return int(df["count"].iloc[0]) if not df.empty else 0

def count_borrowed_books() -> int:
    """Count total borrowed books (loans)."""
    engine = _get_engine()
    if not engine:
        return 0
    query = "SELECT COUNT(*) AS count FROM Loans"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
        return int(df["count"].iloc[0]) if not df.empty else 0

def count_overdue_books() -> int:
    """Count loans overdue (DueDate < today)."""
    engine = _get_engine()
    if not engine:
        return 0
    query = "SELECT COUNT(*) AS count FROM Loans WHERE DueDate < date('now') AND Returned = 0"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
        return int(df["count"].iloc[0]) if not df.empty else 0

def get_friends() -> pd.DataFrame:
    """Fetch all friends with display name."""
    engine = _get_engine()
    if not engine:
        return pd.DataFrame()
    query = text("SELECT FriendID, FName, LName, MaxLoans FROM Friends ORDER BY FName, LName")
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
            df['display'] = df['FName'] + ' ' + df['LName'] + ' (ID: ' + df['FriendID'].astype(str) + ')'
            return df
    except Exception as e:
        st.error(f"Error fetching friends: {e}")
        return pd.DataFrame()

def get_books() -> pd.DataFrame:
    """Fetch available books with display string."""
    engine = _get_engine()
    if not engine:
        return pd.DataFrame()
    query = text("SELECT ISBN, Title FROM Books WHERE IsInStock = 1 ORDER BY Title")
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
            df['display'] = df['Title'] + ' (ISBN: ' + df['ISBN'] + ')'
            return df
    except Exception as e:
        st.error(f"Error fetching available books: {e}")
        return pd.DataFrame()

def get_borrowed_books(friend_id: int) -> pd.DataFrame:
    """Fetch books borrowed by a friend."""
    if not friend_id:
        return pd.DataFrame()
    engine = _get_engine()
    if not engine:
        return pd.DataFrame()
    query = text("""
        SELECT B.ISBN, B.Title FROM Loans L JOIN Books B ON L.ISBN = B.ISBN
        WHERE L.FriendID = :friend_id ORDER BY B.Title
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"friend_id": friend_id})
            df['display'] = df['Title'] + ' (ISBN: ' + df['ISBN'] + ')'
            return df
    except Exception as e:
        st.error(f"Error fetching borrowed books: {e}")
        return pd.DataFrame()

def get_loan_friends() -> pd.DataFrame:
    """Fetch unique friends with current loans."""
    engine = _get_engine()
    if not engine:
        return pd.DataFrame()
    query = text("""
        SELECT DISTINCT FriendID, FName, LName 
        FROM Loans 
        JOIN Friends USING (FriendID) 
        ORDER BY FName, LName
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
            df['display'] = df['FName'] + ' ' + df['LName'] + ' (ID: ' + df['FriendID'].astype(str) + ')'
            return df
    except Exception as e:
        st.error(f"Error fetching friends with loans: {e}")
        return pd.DataFrame()

def get_loan_overdues() -> pd.DataFrame:
    """Fetch overdue loans with friend and book details."""
    engine = _get_engine()
    if not engine:
        return pd.DataFrame()
    query = text("""
        SELECT LoanID, DueDate, FriendID, FName, LName, Title, Loans.ISBN 
        FROM Loans
        JOIN Books USING (ISBN)
        JOIN Friends USING (FriendID)
        WHERE DueDate < datetime('now') AND Returned = 0
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)

def get_friend_contact_info(friend_id: int) -> pd.DataFrame:
    """Fetch contact details for a friend."""
    if not friend_id:
        return pd.DataFrame()
    engine = _get_engine()
    if not engine:
        return pd.DataFrame()
    query = text("SELECT ContactID, type, contact FROM Contacts WHERE FriendID = :friend_id")
    try:
        with engine.connect() as conn:
            return pd.read_sql(query, conn, params={"friend_id": friend_id})
    except Exception as e:
        st.error(f"Error fetching contact info: {e}")
        return pd.DataFrame()

def get_friend_max_loans(friend_id: int):
    """Fetch MaxLoans value for a friend."""
    if not friend_id:
        return None
    engine = _get_engine()
    if not engine:
        return None
    query = text("SELECT MaxLoans FROM Friends WHERE FriendID = :friend_id")
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"friend_id": friend_id})
            if not df.empty:
                return df["MaxLoans"].iloc[0]
            return None
    except Exception:
        return None

def get_daily_reminders() -> pd.DataFrame:
    """Fetch loans with reminder date of today."""
    engine = _get_engine()
    if not engine:
        return pd.DataFrame()
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
        with engine.connect() as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Error fetching reminders: {e}")
        return pd.DataFrame()
