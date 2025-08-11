import streamlit as st
import pandas as pd
from sqlalchemy import text

def create_book(isbn, title, author, genre, book_condition, shelf_location, shelf_row, is_in_stock=1):
    if "engine" not in st.session_state or st.session_state.engine is None:
        st.error("Not connected to the database.")
        return False
        
    engine = st.session_state.engine
    query = text("""
        INSERT INTO Books (ISBN, Title, Author, Genre, BookCondition, IsInStock, ShelfLocation, ShelfRow)
        VALUES (:isbn, :title, :author, :genre, :book_condition, :is_in_stock, :shelf_location, :shelf_row)
    """)
    try:
        with engine.begin() as conn:
            conn.execute(query, {
                "isbn": isbn, "title": title, "author": author, "genre": genre,
                "book_condition": book_condition, "is_in_stock": is_in_stock,
                "shelf_location": shelf_location, "shelf_row": shelf_row
            })
        return True  # ✅ Add this line to confirm success
    except Exception as e:
        st.error(f"Failed to create book: {e}")
        return False

def update_book(isbn, title, author, genre, book_condition, shelf_location, shelf_row):
    if "engine" not in st.session_state or st.session_state.engine is None:
        st.error("Not connected to the database.")
        return False
        
    engine = st.session_state.engine
    query = """
        UPDATE Books
        SET Title = :title,
            Author = :author,
            Genre = :genre,
            BookCondition = :book_condition,
            ShelfLocation = :shelf_location,
            ShelfRow = :shelf_row
        WHERE ISBN = :isbn
    """
    with engine.begin() as conn:
        conn.execute(text(query), {
            "isbn": isbn,
            "title": title,
            "author": author,
            "genre": genre,
            "book_condition": book_condition,
            "shelf_location": shelf_location,
            "shelf_row": shelf_row
        })

def delete_book(isbn):
    if "engine" not in st.session_state or st.session_state.engine is None:
        st.error("Not connected to the database.")
        return False
        
    engine = st.session_state.engine
    delete_query = "DELETE FROM Books WHERE ISBN = :isbn"
    with engine.begin() as conn:
        conn.execute(text(delete_query), {"isbn": isbn})

def create_loan_entry(borrow_date, due_date, return_reminder, isbn, friend_id):
    """Inserts a new loan and updates the book's stock status within a transaction."""
    if "engine" not in st.session_state or st.session_state.engine is None:
        st.error("Not connected to the database.")
        return False
        
    engine = st.session_state.engine
    
    insert_loan_query = text("""
        INSERT INTO Loans (BorrowDate, DueDate, ReturnReminder, ISBN, FriendID)
        VALUES (:borrow_date, :due_date, :return_reminder, :isbn, :friend_id)
    """)
    update_book_status_query = text("UPDATE Books SET IsInStock = 0 WHERE ISBN = :isbn")
    update_friend_loans_query = text("UPDATE Friends SET MaxLoans = (MaxLoans - 1) WHERE FriendID = :friend_id")
    
    loan_data = {
        "borrow_date": borrow_date,
        "due_date": due_date,
        "return_reminder": return_reminder,
        "isbn": isbn,
        "friend_id": friend_id
    }

    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            conn.execute(insert_loan_query, loan_data)
            conn.execute(update_book_status_query, loan_data)
            conn.execute(update_friend_loans_query, loan_data)
            # Commit the transaction if both operations succeed
            transaction.commit()
            return True
        except Exception as e:
            # Roll back the transaction if any error occurs
            transaction.rollback()
            st.error(f"Failed to create loan: {e}")
            return False

def return_book(isbn, friend_id):
    """ Friend returns book. Update book's stock status & delete the loan."""
    if "engine" not in st.session_state or st.session_state.engine is None:
        st.error("Not connected to the database.")
        return False
        
    engine = st.session_state.engine

    delete_loan_query = text("""
        DELETE FROM Loans
        WHERE ISBN = :isbn AND FriendID = :friend_id
    """)

    update_book_status_query = text("UPDATE Books SET IsInStock = 1 WHERE ISBN = :isbn")
    
    update_loan_status_friend_query = text("UPDATE Friends SET MaxLoans = (MaxLoans + 1)  WHERE FriendID = :friend_id")

    params = {"isbn": isbn, "friend_id": friend_id}
    
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            # Delete the selected loan record
            conn.execute(delete_loan_query, params)
            # Update the book's stock status to be available
            conn.execute(update_book_status_query, params)
            # Commit the transaction if both operations succeed
            conn.execute(update_loan_status_friend_query, params)
            # Commit the transaction if both operations succeed
            transaction.commit()
            return True
        except Exception as e:
            # Roll back the transaction if any error occurs
            transaction.rollback()
            st.error(f"Failed to process return: {e}")
            return False
            
def create_friend(fname, lname, max_loans):
    """Inserts a new friend into the database."""
    if "engine" not in st.session_state or st.session_state.engine is None:
        st.error("Not connected to the database.")
        return False
    engine = st.session_state.engine
    query = text("""
        INSERT INTO Friends (FName, LName, MaxLoans)
        VALUES (:fname, :lname, :max_loans)
    """)
    try:
        with engine.begin() as conn:
            conn.execute(query, {"fname": fname, "lname": lname, "max_loans": max_loans})
        return True
    except Exception as e:
        st.error(f"Failed to create friend: {e}")
        return False

def add_friend_with_contacts(fname, lname, max_loans, contacts):
    """Creates a friend and their contact info in a single transaction."""
    if "engine" not in st.session_state or st.session_state.engine is None: return False
    engine = st.session_state.engine
    
    insert_friend_query = text("INSERT INTO Friends (FName, LName, MaxLoans) VALUES (:fname, :lname, :max_loans)")
    insert_contact_query = text("INSERT INTO Contacts (FriendID, type, contact) VALUES (:friend_id, :type, :contact)")

    try:
        with engine.begin() as conn:
            result = conn.execute(insert_friend_query, {"fname": fname, "lname": lname, "max_loans": max_loans})
            friend_id = result.lastrowid
            # Add only contacts that have both a type and info
            valid_contacts = [c for c in contacts if c['type'].strip() and c['contact'].strip()]
            if valid_contacts:
                for contact in valid_contacts:
                    conn.execute(insert_contact_query, {"friend_id": friend_id, "type": contact['type'], "contact": contact['contact']})
        return True
    except Exception as e:
        st.error(f"Failed to add friend: {e}")
        return False


def update_friend(friend_id, fname, lname, max_loans):
    """Updates a friend's main details."""
    if "engine" not in st.session_state or st.session_state.engine is None: return False
    engine = st.session_state.engine
    query = text("UPDATE Friends SET FName = :fname, LName = :lname, MaxLoans = :max_loans WHERE FriendID = :friend_id")
    try:
        with engine.begin() as conn:
            conn.execute(query, {"friend_id": friend_id, "fname": fname, "lname": lname, "max_loans": max_loans})
        return True
    except Exception as e:
        st.error(f"Failed to update friend: {e}")
        return False

def add_contact_to_friend(friend_id, contact_type, contact_info):
    """Adds a new contact to an existing friend."""
    if "engine" not in st.session_state or st.session_state.engine is None: return False
    engine = st.session_state.engine
    query = text("INSERT INTO Contacts (FriendID, type, contact) VALUES (:friend_id, :type, :contact)")
    try:
        with engine.begin() as conn:
            conn.execute(query, {"friend_id": friend_id, "type": contact_type, "contact": contact_info})
        return True
    except Exception as e:
        st.error(f"Failed to add contact: {e}")
        return False

def delete_contact(contact_id):
    """Deletes a single contact entry."""
    if "engine" not in st.session_state or st.session_state.engine is None: return False
    engine = st.session_state.engine
    query = text("DELETE FROM Contacts WHERE ContactID = :contact_id")
    try:
        with engine.begin() as conn:
            conn.execute(query, {"contact_id": contact_id})
        return True
    except Exception as e:
        st.error(f"Failed to delete contact: {e}")
        return False

def delete_friend(friend_id):
    """Deletes a friend and their associated contacts and loans."""
    if "engine" not in st.session_state or st.session_state.engine is None: return False
    engine = st.session_state.engine
    
    # You MUST delete from child tables (Contacts, Loans) before the parent table (Friends)
    # unless you have ON DELETE CASCADE set up in your database.
    delete_contacts_query = text("DELETE FROM Contacts WHERE FriendID = :friend_id")
    delete_loans_query = text("DELETE FROM Loans WHERE FriendID = :friend_id")
    delete_friend_query = text("DELETE FROM Friends WHERE FriendID = :friend_id")
    
    try:
        with engine.begin() as conn:
            conn.execute(delete_contacts_query, {"friend_id": friend_id})
            conn.execute(delete_loans_query, {"friend_id": friend_id})
            conn.execute(delete_friend_query, {"friend_id": friend_id})
        return True
    except Exception as e:
        st.error(f"Failed to delete friend: {e}.")
        return False

def clear_reminder(loan_id):
    """Sets the ReturnReminder to NULL for a given loan to clear it."""
    if "engine" not in st.session_state or st.session_state.engine is None:
        st.error("Not connected to database.")
        return False
    engine = st.session_state.engine
    query = text("UPDATE Loans SET ReturnReminder = NULL WHERE LoanID = :loan_id")
    try:
        with engine.begin() as conn:
            conn.execute(query, {"loan_id": loan_id})
        return True
    except Exception as e:
        st.error(f"Failed to clear reminder: {e}")
        return False