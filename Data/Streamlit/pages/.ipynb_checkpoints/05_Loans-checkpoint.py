import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import datetime, timedelta
import Read
import Write
import library_connection

# --- Page Setup (MUST BE FIRST) ---
st.set_page_config(layout="wide", page_title="Loans")

# --- Check Connection Status ---
if st.session_state.get("db_status") != "Connected":
    st.info("You have been disconnected. Redirecting to login page...")
    st.switch_page("Login.py")

# --- Sidebar ---
st.sidebar.button("Disconnect", on_click=library_connection.disconnect_db)

# --- Flash Message Display Logic (COMES NEXT) ---
if "success_message" in st.session_state:
    st.success(st.session_state.success_message)
    del st.session_state.success_message

# --- Main Page UI ---
st.title("Loans Overview")

# Use st.radio for stateful tab navigation that works on all Streamlit versions
tab_selection = st.radio(
    "Navigation",
    ["📖 See Loans", "➕ Create Loan", "↪️ Return Book", "⁉️ See Overdues"],
    key="main_tabs_radio",
    horizontal=True,
    label_visibility="collapsed"
)

# --- TAB 1: SEE LOANS ---
if tab_selection == "📖 See Loans":
    st.subheader("Active Loans")
    try:
        loans_df = Read.list_loans()
        if not loans_df.empty:
            st.dataframe(loans_df, use_container_width=True)
        else:
            st.info("No active loans found in the library.")
    except Exception as e:
        st.error(f"Error loading loans: {e}")

# --- TAB 2: CREATE LOAN ---
elif tab_selection == "➕ Create Loan":
    st.subheader("Create a new Loan")
    
    # Connection Check
    if st.session_state.get("db_status") != "Connected":
        st.error("You must be connected to the database to view this page.")
        st.stop()

    with st.form("create_loan_form", clear_on_submit=True):
        # Friend Selection
        friends_df = Read.get_friends()
        if not friends_df.empty:
            friend_display_list = friends_df['display'].tolist()
            selected_friend_display_create = st.selectbox(
                "Search for a friend",
                options=friend_display_list, index=None, placeholder="Type to search..."
            )
            selected_friend_id = friends_df[friends_df['display'] == selected_friend_display_create]['FriendID'].iloc[0] if selected_friend_display_create else None
        else:
            st.warning("No friends found.")
            selected_friend_id = None

        # Book Selection
        books_df = Read.get_books()
        if not books_df.empty:
            book_display_list = books_df['display'].tolist()
            selected_book_display_create = st.selectbox(
                "Search for an available book",
                options=book_display_list, index=None, placeholder="Type to search..."
            )
            selected_isbn = books_df[books_df['display'] == selected_book_display_create]['ISBN'].iloc[0] if selected_book_display_create else None
        else:
            st.warning("No available books found.")
            selected_isbn = None

        # Loan Details
        st.subheader("Loan Details")
        today = datetime.now().date()
        borrow_date = st.date_input("Borrow Date", value=today)
        due_date = st.date_input("Due Date", value=today + timedelta(days=14))
        reminder_date = st.date_input("Return Reminder Date", value=due_date - timedelta(days=3))

        # ✅ The button is no longer disabled
        submitted = st.form_submit_button("Create Loan")
        if submitted:
            # 1. First, validate that selections were made
            if not (selected_friend_id and selected_isbn):
                st.error("Please select both a friend and a book.")
            else:
                # 2. Now, check the friend's loan limit
                max_loans = Read.get_friend_max_loans(friend_id=selected_friend_id)
                if max_loans is not None and max_loans <= 0:
                    st.error("Max Amount Of Loans Was Reached for this friend. Loan not created.")
                else:
                    # 3. If all checks pass, create the loan
                    if Write.create_loan_entry(borrow_date, due_date, reminder_date, selected_isbn, selected_friend_id):
                        st.session_state.success_message = f"Loan created successfully for {selected_friend_display_create}!"
                        st.cache_data.clear()
                        st.rerun()


# --- TAB 3: RETURN BOOK ---
elif tab_selection == "↪️ Return Book":
    st.subheader("Return a Book")

    # Connection Check
    if st.session_state.get("db_status") != "Connected":
        st.error("You must be connected to the database to view this page.")
        st.stop()

    # Get a DataFrame of all active loans
    loans_df = Read.list_loans()

    if not loans_df.empty:
        # Create a user-friendly display column for the dropdown
        loans_df['display'] = "Loan #" + loans_df['LoanID'].astype(str) + ": '" + loans_df['Title'] + \
                              "' to " + loans_df['FName'] + " " + loans_df['LName']
        
        loan_display_list = loans_df['display'].tolist()

        # Create a single dropdown to select the loan
        selected_loan_display = st.selectbox(
            "Select the loan to return",
            options=loan_display_list,
            index=None,
            placeholder="Select a loan..."
        )

        # Form for the final action button
        with st.form("return_book_form"):
            submitted = st.form_submit_button("Confirm Return")
            if submitted:
                if selected_loan_display:
                    # Get the ISBN and FriendID from the selected loan
                    selected_loan = loans_df[loans_df['display'] == selected_loan_display].iloc[0]
                    selected_isbn = selected_loan['ISBN']
                    selected_friend_id = selected_loan['FriendID']

                    if Write.return_book(isbn=selected_isbn, friend_id=selected_friend_id):
                        st.session_state.success_message = "Book return processed successfully!"
                        st.rerun()
                else:
                    st.error("Please select a loan to return.")
    else:
        st.info("There are no active loans to return.")
        
# --- TAB 4: SEE OVERDUES ---
if tab_selection == "⁉️ See Overdues":
    st.subheader("Overdue Loans")
    try:
        overdues_df = Read.get_loan_overdues()
        if not overdues_df.empty:
            st.dataframe(overdues_df, use_container_width=True, hide_index=True)
            
            st.markdown("---") # Add a visual separator
            st.subheader("Get Contact Information")

            # Create a unique list of friends from the overdues table
            friends_with_overdues = overdues_df[['FriendID', 'FName', 'LName']].drop_duplicates()
            friends_with_overdues['display'] = friends_with_overdues['FName'] + ' ' + friends_with_overdues['LName'] + ' (ID: ' + friends_with_overdues['FriendID'].astype(str) + ')'
            
            # Create the dropdown
            selected_friend_display = st.selectbox(
                "Select a friend to view their contact details",
                options=friends_with_overdues['display'].tolist(),
                index=None,
                placeholder="Select a friend..."
            )

            # If a friend is selected, fetch and display their contact info
            if selected_friend_display:
                # Find the ID of the selected friend
                selected_friend_id = friends_with_overdues[friends_with_overdues['display'] == selected_friend_display]['FriendID'].iloc[0]
                
                contact_df = Read.get_friend_contact_info(friend_id=selected_friend_id)
                if not contact_df.empty:
                    st.write("**Contact Details:**")
                    # Display each contact detail in its own column
                    cols = st.columns(len(contact_df))
                    for idx, col in enumerate(cols):
                        contact_type = contact_df.iloc[idx]['type']
                        contact_value = contact_df.iloc[idx]['contact']
                        col.metric(label=contact_type.capitalize(), value=contact_value)
                else:
                    st.warning("No contact information found for this friend.")
        else:
            st.info("🎉 No overdue loans found!")
    except Exception as e:
        st.error(f"Error loading overdues: {e}")
