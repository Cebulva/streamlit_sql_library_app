# Read.py
import pandas as pd
import streamlit as st
from sqlalchemy import text
from library_connection import engine


def _run_query_df(sql, params=None):
    """Run a SQL query and return a Pandas DataFrame with a fresh connection."""
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(sql), conn, params=params)
    except Exception as e:
        st.error(f"Database read error: {e}")
        return pd.DataFrame()


def count_books():
    """Return the number of books in the Books table."""
    df = _run_query_df("SELECT COUNT(*) AS count FROM Books")
    if not df.empty:
        return df["count"].iloc[0]
    return 0


def list_loans():
    """Return a DataFrame of active loans."""
    sql = """
    SELECT Loans.LoanID, Books.ISBN, Books.Title, Friends.FName, Friends.LName, 
           Loans.BorrowDate, Loans.DueDate, Loans.ReminderDate
    FROM Loans
    JOIN Books ON Loans.ISBN = Books.ISBN
    JOIN Friends ON Loans.FriendID = Friends.FriendID
    WHERE Loans.Returned = 0
    ORDER BY Loans.DueDate ASC
    """
    return _run_query_df(sql)


def get_friends():
    """Return a list of friends with display names for dropdowns."""
    sql = """
    SELECT FriendID, FName || ' ' || LName AS display
    FROM Friends
    ORDER BY LName, FName
    """
    return _run_query_df(sql)


def get_books():
    """Return a list of available books (not currently on loan)."""
    sql = """
    SELECT ISBN, Title || ' by ' || Author AS display
    FROM Books
    WHERE ISBN NOT IN (
        SELECT ISBN FROM Loans WHERE Returned = 0
    )
    ORDER BY Title
    """
    return _run_query_df(sql)


def get_friend_max_loans(friend_id):
    """Return the remaining loan capacity for a friend."""
    sql = """
    SELECT MaxLoans - COUNT(l.ISBN) AS remaining_loans
    FROM Friends f
    LEFT JOIN Loans l ON f.FriendID = l.FriendID AND l.Returned = 0
    WHERE f.FriendID = :fid
    GROUP BY f.MaxLoans
    """
    df = _run_query_df(sql, {"fid": friend_id})
    if not df.empty:
        return df["remaining_loans"].iloc[0]
    return None


def get_loan_overdues():
    """Return loans that are overdue."""
    sql = """
    SELECT Loans.LoanID, Books.Title, Friends.FName, Friends.LName,
           Loans.BorrowDate, Loans.DueDate
    FROM Loans
    JOIN Books ON Loans.ISBN = Books.ISBN
    JOIN Friends ON Loans.FriendID = Friends.FriendID
    WHERE Loans.Returned = 0
      AND Loans.DueDate < DATE('now')
    ORDER BY Loans.DueDate ASC
    """
    return _run_query_df(sql)


def get_friend_contact_info(friend_id):
    """Return contact information for a specific friend."""
    sql = """
    SELECT type, contact
    FROM Contacts
    WHERE FriendID = :fid
    """
    return _run_query_df(sql, {"fid": friend_id})

def count_borrowed_books():
    """Return the total number of books currently on loan (not returned)."""
    sql = """
    SELECT COUNT(*) AS count
    FROM Loans
    WHERE Returned = 0
    """
    df = _run_query_df(sql)
    if not df.empty:
        return df["count"].iloc[0]
    return 0