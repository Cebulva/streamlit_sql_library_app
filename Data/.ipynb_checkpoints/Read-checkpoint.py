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
        SELECT B.ISBN, B.Title F
