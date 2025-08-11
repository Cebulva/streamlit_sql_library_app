import streamlit as st
import library_connection
import Read
import Write
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="Liane's Library",
    page_icon="📖"
)

# --- Initialize State for Expanders ---
for key in ["show_add_book", "show_add_friend", "show_create_loan", "show_return_book"]:
    if key not in st.session_state:
        st.session_state[key] = False

# --- Check Connection Status ---
if st.session_state.get("db_status") != "Connected":
    st.info("You have been disconnected. Redirecting to login page...")
    st.switch_page("Login.py")

# --- Sidebar ---
st.sidebar.button("Disconnect", on_click=library_connection.disconnect_db)

# --- Flash Message ---
if "success_message" in st.session_state:
    st.success(st.session_state.pop("success_message"))

# --- Page Content ---
st.markdown("<h1 style='text-align: center;'>📚 📖 📕 📚 📘 📙 Welcome To Liane's Library 📗 📖 📙 📚 📘 📖</h1>", unsafe_allow_html=True)

# --- METRICS ---
with st.expander("Library Overview", expanded=True):
    total_books = Read.count_books()
    borrowed_books = Read.count_borrowed_books()
    available_books = total_books - borrowed_books
    overdue_books = Read.count_overdue_books()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Books", total_books)
    col2.metric("Borrowed", borrowed_books)
    col3.metric("Available", available_books)
    col4.metric("Overdue", overdue_books)

st.markdown("---")
st.subheader("Daily Reminders 🗓️")

reminders_df = Read.get_daily_reminders()

if reminders_df.empty:
    st.info("No reminders for today. All caught up! ✅")
else:
    grouped = reminders_df.groupby(['LoanID', 'FriendID', 'FName', 'LName', 'Title', 'DueDate'])
    
    st.warning(f"You have {len(grouped)} reminder(s) to send today:")
    
    for (loan_id, friend_id, fname, lname, title, due_date), contacts in grouped:
        st.info(f"**{fname} {lname}** needs a reminder about returning **'{title}'**. It's due on **{due_date.strftime('%Y-%m-%d')}**.")
        
        contact_info = contacts[['type', 'contact']].drop_duplicates().reset_index(drop=True)
        st.write("**Contact Details:**")
        
        # Display contact info in columns
        contact_cols = st.columns(len(contact_info))
        for idx, col in enumerate(contact_cols):
            contact_type = contact_info.iloc[idx]['type']
            contact_value = contact_info.iloc[idx]['contact']
            col.metric(label=contact_type.capitalize(), value=contact_value)
        
        # --- Add buttons in columns to place them side-by-side ---
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
            # ✅ Add the st.link_button here
            st.link_button(
                "Send Email 📧", 
                "https://mail.google.com/mail/u/0/#inbox?compose=new",
                use_container_width=True
            )
            
        st.markdown("---")

st.subheader("Quick Actions")

# --- Define a callback to manage which expander is active ---
def set_active_expander(form_name):
    for key in ["show_add_book", "show_add_friend", "show_create_loan", "show_return_book"]:
        st.session_state[key] = False
    st.session_state[form_name] = True

# --- Buttons to show the expander forms ---
col1, col2, col3, col4 = st.columns(4)
col1.button("➕ Create Loan", on_click=set_active_expander, args=("show_create_loan",), use_container_width=True)
col2.button("↪️ Return Book", on_click=set_active_expander, args=("show_return_book",), use_container_width=True)
col3.button("📚 Add Book", on_click=set_active_expander, args=("show_add_book",), use_container_width=True)
col4.button("🧑‍🤝‍🧑 Add Friend", on_click=set_active_expander, args=("show_add_friend",), use_container_width=True)

# --- EXPANDER FOR CREATING A LOAN ---
if st.session_state.show_create_loan:
    with st.expander("Create a New Loan", expanded=True):
        with st.form("create_loan_form", clear_on_submit=True):
            friends_df = Read.get_friends()
            friend_display_list = friends_df['display'].tolist()
            selected_friend_display = st.selectbox("Search for a friend", options=friend_display_list, index=None, placeholder="Select a friend...")
            
            books_df = Read.get_books()
            book_display_list = books_df['display'].tolist()
            selected_book_display = st.selectbox("Search for an available book", options=book_display_list, index=None, placeholder="Select a book...")

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
                        st.rerun()
                else:
                    st.error("Please select both a friend and a book.")

# --- EXPANDER FOR RETURNING A BOOK ---
if st.session_state.show_return_book:
    with st.expander("Return a Book", expanded=True):
        loans_df = Read.list_loans()
        if not loans_df.empty:
            loans_df['display'] = "Loan #" + loans_df['LoanID'].astype(str) + ": '" + loans_df['Title'] + "' to " + loans_df['FName'] + " " + loans_df['LName']
            loan_display_list = loans_df['display'].tolist()
            selected_loan_display = st.selectbox("Select the loan to return", options=loan_display_list, index=None, placeholder="Select a loan...")
            
            with st.form("return_book_form", clear_on_submit=True):
                if st.form_submit_button("Confirm Return"):
                    if selected_loan_display:
                        selected_loan = loans_df[loans_df['display'] == selected_loan_display].iloc[0]
                        if Write.return_book(isbn=selected_loan['ISBN'], friend_id=selected_loan['FriendID']):
                            st.session_state.success_message = "Book return processed successfully!"
                            st.cache_data.clear()
                            st.rerun()
                    else:
                        st.error("Please select a loan to return.")
        else:
            st.info("There are no active loans to return.")

# --- EXPANDER FOR ADDING A BOOK ---
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
                        st.rerun()

# --- EXPANDER FOR ADDING A FRIEND ---
if st.session_state.show_add_friend:
    with st.expander("Add a New Friend", expanded=True):
        
        # --- State initialization for the HOME page form ---
        if 'home_new_contacts' not in st.session_state:
            st.session_state.home_new_contacts = [{"type": "", "contact": ""}]
        if 'home_add_fname' not in st.session_state:
            st.session_state.home_add_fname = ""
        if 'home_add_lname' not in st.session_state:
            st.session_state.home_add_lname = ""
        if 'home_add_maxloans' not in st.session_state:
            st.session_state.home_add_maxloans = 2

        # --- Define callbacks for the HOME page form ---
        def reset_home_add_friend_form():
            st.session_state.home_new_contacts = [{"type": "", "contact": ""}]
            st.session_state.home_add_fname = ""
            st.session_state.home_add_lname = ""
            st.session_state.home_add_maxloans = 2
            if "home_add_type_0" in st.session_state:
                st.session_state.home_add_type_0 = ""
            if "home_add_contact_0" in st.session_state:
                st.session_state.home_add_contact_0 = ""

        def add_home_contact_row():
            st.session_state.home_new_contacts.append({"type": "", "contact": ""})

        def submit_home_add_friend():
            final_contacts = []
            for i in range(len(st.session_state.home_new_contacts)):
                contact_type = st.session_state.get(f"home_add_type_{i}", "")
                contact_info = st.session_state.get(f"home_add_contact_{i}", "")
                final_contacts.append({"type": contact_type, "contact": contact_info})
            
            if not (st.session_state.home_add_fname and st.session_state.home_add_lname):
                st.warning("First and Last Name are required.")
            else:
                if Write.add_friend_with_contacts(st.session_state.home_add_fname, st.session_state.home_add_lname, st.session_state.home_add_maxloans, final_contacts):
                    st.session_state.success_message = "Friend added successfully!"
                    reset_home_add_friend_form() 
                    st.cache_data.clear()
                    st.session_state.show_add_friend = False # Close expander

        # --- Action Buttons ---
        col1, col2 = st.columns(2)
        with col1:
            st.button("Add additional contact information", on_click=add_home_contact_row, use_container_width=True, key="home_add_contact_btn")
        with col2:
            st.button("Reset Form", on_click=reset_home_add_friend_form, use_container_width=True, key="home_reset_btn")

        st.markdown("---")

        # --- Final Submission Form ---
        with st.form("add_friend_form_home"):
            st.write("**Friend's Details**")
            c1, c2 = st.columns(2)
            st.text_input("First Name", key="home_add_fname")
            st.text_input("Last Name", key="home_add_lname")
            st.number_input("Max Loans", min_value=0, step=1, key="home_add_maxloans")
            
            st.markdown("---")
            st.write("**Contact Information**")
            
            for i in range(len(st.session_state.home_new_contacts)):
                c1, c2 = st.columns(2)
                c1.text_input("Contact Type", key=f"home_add_type_{i}")
                c2.text_input("Contact Info", key=f"home_add_contact_{i}")
            
            st.form_submit_button("💾  Save Friend", on_click=submit_home_add_friend)