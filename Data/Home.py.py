# Home.py
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import Read
import Write

# --- Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="Liane's Library",
    page_icon="📖"
)

# --- Initialize Session State ---
for key in ["show_add_book", "show_add_friend", "show_create_loan", "show_return_book"]:
    if key not in st.session_state:
        st.session_state[key] = False

if "db_status" not in st.session_state:
    st.session_state.db_status = "Connected"

# --- Sidebar ---
st.sidebar.title("Liane's Library")

# --- Success Message Flash ---
if "success_message" in st.session_state:
    st.success(st.session_state.pop("success_message"))

# --- Page Title ---
st.markdown(
    "<h1 style='text-align: center;'>📚 📖 📕 📚 📘 📙 Welcome To Liane's Library 📗 📖 📙 📚 📘 📖</h1>",
    unsafe_allow_html=True
)

# --- Daily Reminders Section ---
st.subheader("Daily Reminders 🗓️")
reminders_df = Read.get_daily_reminders()

if reminders_df.empty:
    st.info("No reminders for today. All caught up! ✅")
else:
    grouped = reminders_df.groupby(['LoanID', 'FriendID', 'FName', 'LName', 'Title', 'DueDate'])
    st.warning(f"You have {len(grouped)} reminder(s) to send today:")

    for (loan_id, friend_id, fname, lname, title, due_date), contacts in grouped:
        # Ensure due_date is a proper datetime object
        if pd.isnull(due_date):
            due_date_str = "unknown due date"
        elif isinstance(due_date, str):
            try:
                due_date_dt = pd.to_datetime(due_date)
                due_date_str = due_date_dt.strftime('%Y-%m-%d')
            except Exception:
                due_date_str = due_date  # fallback to string itself
        else:
            due_date_str = due_date.strftime('%Y-%m-%d')

        st.info(f"**{fname} {lname}** needs a reminder about returning **'{title}'**. It's due on **{due_date_str}**.")
        
        contact_info = contacts[['type', 'contact']].drop_duplicates().reset_index(drop=True)

        contact_cols = st.columns(len(contact_info))
        for idx, col in enumerate(contact_cols):
            contact_type = contact_info.iloc[idx]['type']
            contact_value = contact_info.iloc[idx]['contact']
            col.metric(label=contact_type.capitalize(), value=contact_value)

        col1, col2 = st.columns(2)
        with col1:
            def clear_and_refresh(l_id):
                if Write.clear_reminder(l_id):
                    st.cache_data.clear()

            st.button(
                "Clear Reminder",
                key=f"clear_{loan_id}",
                on_click=clear_and_refresh,
                args=(loan_id,),
                use_container_width=True
            )
        with col2:
            st.link_button(
                "Send Email 📧",
                "https://mail.google.com/mail/u/0/#inbox?compose=new",
                use_container_width=True
            )
        st.markdown("---")

# --- Quick Actions Section ---
st.subheader("Quick Actions")

def set_active_expander(form_name):
    for key in ["show_add_book", "show_add_friend", "show_create_loan", "show_return_book"]:
        st.session_state[key] = False
    st.session_state[form_name] = True

col1, col2, col3, col4 = st.columns(4)
col1.button("➕ Create Loan", on_click=set_active_expander, args=("show_create_loan",), use_container_width=True)
col2.button("↪️ Return Book", on_click=set_active_expander, args=("show_return_book",), use_container_width=True)
col3.button("📚 Add Book", on_click=set_active_expander, args=("show_add_book",), use_container_width=True)
col4.button("🧑‍🤝‍🧑 Add Friend", on_click=set_active_expander, args=("show_add_friend",), use_container_width=True)

# --- Create Loan Expander ---
if st.session_state.show_create_loan:
    with st.expander("Create a New Loan", expanded=True):
        with st.form("create_loan_form", clear_on_submit=True):
            friends_df = Read.get_friends()
            friend_display_list = friends_df['display'].tolist()
            selected_friend_display = st.selectbox("Search for a friend", options=friend_display_list, placeholder="Select a friend...")

            books_df = Read.get_books()
            book_display_list = books_df['display'].tolist()
            selected_book_display = st.selectbox("Search for an available book", options=book_display_list, placeholder="Select a book...")

            today = datetime.now().date()
            borrow_date = st.date_input("Borrow Date", value=today)
            due_date = st.date_input("Due Date", value=today + timedelta(days=14))
            reminder_date = st.date_input("Return Reminder Date", value=due_date - timedelta(days=3))

            if st.form_submit_button("Create Loan"):
                if selected_friend_display and selected_book_display:
                    selected_friend_id = friends_df[friends_df['display'] == selected_friend_display]['FriendID'].iloc[0]
                    selected_isbn = books_df[books_df['display'] == selected_book_display]['ISBN'].iloc[0]
                    if Write.create_loan_entry(borrow_date, due_date, reminder_date, selected_isbn, selected_friend_id):
                        st.session_state.success_message = "Loan created successfully!"
                        st.cache_data.clear()
                        st.experimental_rerun()
                else:
                    st.error("Please select both a friend and a book.")

# --- Return Book Expander ---
if st.session_state.show_return_book:
    with st.expander("Return a Book", expanded=True):
        loans_df = Read.list_loans()
        if not loans_df.empty:
            loans_df['display'] = (
                "Loan #" + loans_df['LoanID'].astype(str) +
                ": '" + loans_df['Title'] + "' to " +
                loans_df['FName'] + " " + loans_df['LName']
            )
            loan_display_list = loans_df['display'].tolist()
            selected_loan_display = st.selectbox("Select the loan to return", options=loan_display_list, placeholder="Select a loan...")

            with st.form("return_book_form", clear_on_submit=True):
                if st.form_submit_button("Confirm Return"):
                    if selected_loan_display:
                        selected_loan = loans_df[loans_df['display'] == selected_loan_display].iloc[0]
                        if Write.return_book(isbn=selected_loan['ISBN'], friend_id=selected_loan['FriendID']):
                            st.session_state.success_message = "Book return processed successfully!"
                            st.cache_data.clear()
                            st.experimental_rerun()
                    else:
                        st.error("Please select a loan to return.")
        else:
            st.info("There are no active loans to return.")

# --- Add Book Expander ---
if st.session_state.show_add_book:
    with st.expander("Add a New Book", expanded=True):
        with st.form("add_book_form", clear_on_submit=True):
            isbn = st.text_input("ISBN")
            title = st.text_input("Title")
            author = st.text_input("Author")
            genre = st.text_input("Genre")
            book_condition = st.selectbox("Book Condition", ["Excellent", "Good", "Fair"])
            shelf_location = st.selectbox("Shelf Location", ["A1", "B1", "C1"])
            shelf_row = st.selectbox("Row Number", ["1", "2", "3"])

            if st.form_submit_button("💾 Save Book"):
                if not all([isbn, title, author, genre]):
                    st.error("Please fill in all required fields.")
                elif Read.book_exists(isbn):
                    st.warning(f"A book with ISBN {isbn} already exists.")
                else:
                    if Write.create_book(isbn, title, author, genre, book_condition, shelf_location, int(shelf_row)):
                        st.session_state.success_message = f"Book '{title}' added successfully!"
                        st.cache_data.clear()
                        st.experimental_rerun()

# --- Add Friend Expander ---
if st.session_state.show_add_friend:
    with st.expander("Add a New Friend", expanded=True):
        if 'home_new_contacts' not in st.session_state:
            st.session_state.home_new_contacts = [{"type": "", "contact": ""}]
        if 'home_add_fname' not in st.session_state:
            st.session_state.home_add_fname = ""

        # Add your friend form implementation here as needed
