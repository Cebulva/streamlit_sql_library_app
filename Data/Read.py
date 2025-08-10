import streamlit as st
import pandas as pd
from sqlalchemy import (
    create_engine, select, text, Table, MetaData, and_, func
)
from sqlalchemy.engine import Engine
from typing import Optional

# Centralized engine singleton initializer
def get_engine() -> Optional[Engine]:
    if not hasattr(get_engine, "_engine"):
        import os
        DB_PATH = os.path.join(os.path.dirname(__file__), "library.db")
        try:
            get_engine._engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
        except Exception as e:
            st.error(f"Failed to create DB engine: {e}")
            return None
    return get_engine._engine


metadata = MetaData()
engine = get_engine()

# Reflect tables once for reuse
Books = Table("Books", metadata, autoload_with=engine) if engine else None
Loans = Table("Loans", metadata, autoload_with=engine) if engine else None
Friends = Table("Friends", metadata, autoload_with=engine) if engine else None
Contacts = Table("Contacts", metadata, autoload_with=engine) if engine else None


def _get_engine() -> Optional[Engine]:
    """Get the SQLAlchemy engine or report an error."""
    eng = get_engine()
    if eng is None:
        st.error("Database connection not found.")
    return eng


def list_books() -> pd.DataFrame:
    """Retrieve all books from the database."""
    eng = _get_engine()
    if not eng or Books is None:
        return pd.DataFrame()
    stmt = select(Books)
    with eng.connect() as conn:
        return pd.read_sql(stmt, conn)


def list_loans() -> pd.DataFrame:
    """Retrieve all active loans with friend and book details."""
    eng = _get_engine()
    if not eng or Loans is None or Books is None or Friends is None:
        return pd.DataFrame()
    j = Loans.join(Books, Loans.c.ISBN == Books.c.ISBN).join(Friends, Loans.c.FriendID == Friends.c.FriendID)
    stmt = select(
        Loans.c.LoanID,
        Loans.c.FriendID,
        Friends.c.FName,
        Friends.c.LName,
        Loans.c.BorrowDate,
        Loans.c.DueDate,
        Loans.c.ReturnReminder,
        Books.c.Title,
        Loans.c.ISBN
    ).select_from(j)
    with eng.connect() as conn:
        return pd.read_sql(stmt, conn)


def loan_exists(LoanID: int) -> bool:
    """Check if a loan with LoanID exists."""
    eng = _get_engine()
    if not eng or Loans is None:
        return False
    query = select(Loans.c.LoanID).where(Loans.c.LoanID == LoanID).limit(1)
    with eng.connect() as conn:
        return conn.execute(query).fetchone() is not None


def book_exists(isbn: str) -> bool:
    """Check if a book with ISBN exists."""
    eng = _get_engine()
    if not eng or Books is None:
        return False
    query = select(Books.c.ISBN).where(Books.c.ISBN == isbn).limit(1)
    with eng.connect() as conn:
        return conn.execute(query).fetchone() is not None


def read_all_books() -> pd.DataFrame:
    """Read all books ordered by title."""
    eng = _get_engine()
    if not eng or Books is None:
        return pd.DataFrame()
    stmt = select(Books).order_by(Books.c.Title)
    with eng.connect() as conn:
        return pd.read_sql(stmt, conn)


def read_books() -> pd.DataFrame:
    """Read books with formatted location and condition."""
    eng = _get_engine()
    if not eng or Books is None:
        return pd.DataFrame()
    query = text("""
        SELECT 
            ISBN, 
            Title, 
            Author, 
            Genre, 
            IsInStock, 
            BookCondition AS "Condition", 
            ShelfLocation || ' ' || ShelfRow AS Location 
        FROM Books 
        ORDER BY Title
    """)
    with eng.connect() as conn:
        return pd.read_sql(query, conn)


def count_borrowed_books() -> int:
    """Count total borrowed books (loans)."""
    eng = _get_engine()
    if not eng or Loans is None:
        return 0
    query = select(func.count()).select_from(Loans)
    with eng.connect() as conn:
        result = conn.execute(query)
        return result.scalar_one()


def count_borrowed_books() -> int:
    """Count total borrowed books (loans)."""
    eng = _get_engine()
    if not eng or Loans is None:
        return 0
    query = select([text("COUNT(*)")]).select_from(Loans)
    with eng.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM Loans"))
        return result.scalar_one()


def count_overdue_books() -> int:
    """Count loans overdue (DueDate < today and not returned)."""
    eng = _get_engine()
    if not eng or Loans is None:
        return 0
    query = text("""
        SELECT COUNT(*) FROM Loans
        WHERE DueDate < date('now') AND Returned = 0
    """)
    with eng.connect() as conn:
        result = conn.execute(query)
        return result.scalar_one()


def get_friends() -> pd.DataFrame:
    """Fetch all friends with display name."""
    eng = _get_engine()
    if not eng or Friends is None:
        return pd.DataFrame()
    query = select(Friends).order_by(Friends.c.FName, Friends.c.LName)
    try:
        with eng.connect() as conn:
            df = pd.read_sql(query, conn)
            df['display'] = df['FName'] + ' ' + df['LName'] + ' (ID: ' + df['FriendID'].astype(str) + ')'
            return df
    except Exception as e:
        st.error(f"Error fetching friends: {e}")
        return pd.DataFrame()


def get_books() -> pd.DataFrame:
    """Fetch available books with display string."""
    eng = _get_engine()
    if not eng or Books is None:
        return pd.DataFrame()
    query = select(Books.c.ISBN, Books.c.Title).where(Books.c.IsInStock == 1).order_by(Books.c.Title)
    try:
        with eng.connect() as conn:
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
    eng = _get_engine()
    if not eng or Loans is None or Books is None:
        return pd.DataFrame()
    j = Loans.join(Books, Loans.c.ISBN == Books.c.ISBN)
    stmt = select(Books.c.ISBN, Books.c.Title).select_from(j).where(Loans.c.FriendID == friend_id).order_by(Books.c.Title)
    try:
        with eng.connect() as conn:
            df = pd.read_sql(stmt, conn)
            df['display'] = df['Title'] + ' (ISBN: ' + df['ISBN'] + ')'
            return df
    except Exception as e:
        st.error(f"Error fetching borrowed books: {e}")
        return pd.DataFrame()


def get_loan_friends() -> pd.DataFrame:
    """Fetch unique friends with current loans."""
    eng = _get_engine()
    if not eng or Loans is None or Friends is None:
        return pd.DataFrame()
    j = Loans.join(Friends, Loans.c.FriendID == Friends.c.FriendID)
    stmt = select(
        Friends.c.FriendID,
        Friends.c.FName,
        Friends.c.LName
    ).select_from(j).distinct().order_by(Friends.c.FName, Friends.c.LName)
    try:
        with eng.connect() as conn:
            df = pd.read_sql(stmt, conn)
            df['display'] = df['FName'] + ' ' + df['LName'] + ' (ID: ' + df['FriendID'].astype(str) + ')'
            return df
    except Exception as e:
        st.error(f"Error fetching friends with loans: {e}")
        return pd.DataFrame()


def get_loan_overdues() -> pd.DataFrame:
    """Fetch overdue loans with friend and book details."""
    eng = _get_engine()
    if not eng or Loans is None or Books is None or Friends is None:
        return pd.DataFrame()
    j = Loans.join(Books, Loans.c.ISBN == Books.c.ISBN).join(Friends, Loans.c.FriendID == Friends.c.FriendID)
    stmt = select(
        Loans.c.LoanID,
        Loans.c.DueDate,
        Friends.c.FriendID,
        Friends.c.FName,
        Friends.c.LName,
        Books.c.Title,
        Loans.c.ISBN
    ).select_from(j).where(
        and_(
            Loans.c.DueDate < text("date('now')"),
            Loans.c.Returned == 0
        )
    )
    with eng.connect() as conn:
        return pd.read_sql(stmt, conn)


def get_friend_contact_info(friend_id: int) -> pd.DataFrame:
    """Fetch contact details for a friend."""
    if not friend_id:
        return pd.DataFrame()
    eng = _get_engine()
    if not eng or Contacts is None:
        return pd.DataFrame()
    query = select(Contacts).where(Contacts.c.FriendID == friend_id)
    try:
        with eng.connect() as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Error fetching contact info: {e}")
        return pd.DataFrame()


def get_friend_max_loans(friend_id: int) -> Optional[int]:
    """Fetch MaxLoans value for a friend."""
    if not friend_id:
        return None
    eng = _get_engine()
    if not eng or Friends is None:
        return None
    query = select(Friends.c.MaxLoans).where(Friends.c.FriendID == friend_id).limit(1)
    try:
        with eng.connect() as conn:
            df = pd.read_sql(query, conn)
            if not df.empty:
                return int(df["MaxLoans"].iloc[0])
            return None
    except Exception:
        return None


def get_daily_reminders() -> pd.DataFrame:
    """Fetch loans with reminder date of today."""
    eng = _get_engine()
    if not eng or Loans is None or Friends is None or Books is None or Contacts is None:
        return pd.DataFrame()
    j = Loans.join(Friends, Loans.c.FriendID == Friends.c.FriendID)\
             .join(Books, Loans.c.ISBN == Books.c.ISBN)\
             .join(Contacts, Loans.c.FriendID == Contacts.c.FriendID)
    stmt = select(
        Loans.c.LoanID,
        Loans.c.DueDate,
        Friends.c.FriendID,
        Friends.c.FName,
        Friends.c.LName,
        Books.c.Title,
        Contacts.c.type,
        Contacts.c.contact
    ).select_from(j).where(
        text("date(Loans.ReturnReminder) = date('now')")
    )
    try:
        with eng.connect() as conn:
            return pd.read_sql(stmt, conn)
    except Exception as e:
        st.error(f"Error fetching reminders: {e}")
        return pd.DataFrame()


def can_borrow_more(friend_id: int) -> bool:
    """Check if friend can borrow more books according to MaxLoans."""
    max_loans = get_friend_max_loans(friend_id)
    if max_loans is None:
        return False
    eng = _get_engine()
    if not eng or Loans is None:
        return False
    query = select(Loans).where(
        and_(
            Loans.c.FriendID == friend_id,
            Loans.c.Returned == 0
        )
    )
    with eng.connect() as conn:
        current_loans = conn.execute(query).rowcount
        return current_loans < max_loans
