import streamlit as st
import pandas as pd
import Read
import Write
import library_connection # ✅ Add this line

# --- PAGE CONFIG ---
st.set_page_config("📚 Manage Books", layout="wide")

# --- Check Connection Status ---
if st.session_state.get("db_status") != "Connected":
    st.info("You have been disconnected. Redirecting to login page...")
    st.switch_page("Login.py")

# --- Sidebar ---
st.sidebar.button("Disconnect", on_click=library_connection.disconnect_db)

# --- Flash Message ---
if "success_message" in st.session_state:
    st.success(st.session_state.pop("success_message"))

st.title("Books Overview")

# --- NAVIGATION ---
# ✅ Replace st.tabs with a stateful st.radio widget
selection = st.radio(
    "Navigation",
    ["🔎 Search Books", "📚 Manage Books"],
    horizontal=True,
    label_visibility="collapsed",
    key="books_nav" # Use a key to save the state
)

# === MANAGE BOOKS ===
if selection == "📚 Manage Books":
    mode = st.radio("Select Mode", ["➕ Add Book", "✏️ Edit Book", "🗑️ Delete Book"], horizontal=True, key="manage_mode")

    if mode == "➕ Add Book":
        with st.form("add_book_form", clear_on_submit=True):
            st.subheader("Add a New Book")
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
                    Write.create_book(isbn, title, author, genre, book_condition, shelf_location, int(shelf_row))
                    st.session_state.success_message = f"Book '{title}' added successfully!"
                    st.rerun()

    elif mode == "✏️ Edit Book":
        st.subheader("Edit an Existing Book")
        all_books = Read.read_all_books()

        if not all_books.empty:
            options = all_books.apply(lambda row: f"{row['Title']} (ISBN: {row['ISBN']})", axis=1).tolist()
            selected_display = st.selectbox(
                "Select a book to edit",
                options=options,
                index=None,
                placeholder="Search or select a book from the list..."
            )

            if selected_display:
                selected_book = all_books[all_books.apply(lambda r: f"{r['Title']} (ISBN: {r['ISBN']})", axis=1) == selected_display].iloc[0]
                with st.form("edit_book_form"):
                    st.write(f"Editing: **{selected_book['Title']}**")
                    title = st.text_input("Title", value=selected_book["Title"])
                    author = st.text_input("Author", value=selected_book["Author"])
                    genre = st.text_input("Genre", value=selected_book["Genre"])
                    condition_opts = ["Excellent", "Good", "Fair"]
                    cond_index = condition_opts.index(selected_book["BookCondition"]) if selected_book["BookCondition"] in condition_opts else 0
                    book_condition = st.selectbox("Book Condition", condition_opts, index=cond_index)
                    loc_opts = ["A1", "B1", "C1"]
                    loc_index = loc_opts.index(selected_book["ShelfLocation"]) if selected_book["ShelfLocation"] in loc_opts else 0
                    shelf_location = st.selectbox("Shelf Location", loc_opts, index=loc_index)
                    row_opts = ["1", "2", "3"]
                    row_index = row_opts.index(str(selected_book["ShelfRow"])) if str(selected_book["ShelfRow"]) in row_opts else 0
                    shelf_row = st.selectbox("Row Number", row_opts, index=row_index)

                    if st.form_submit_button("💾 Update Book"):
                        Write.update_book(selected_book["ISBN"], title, author, genre, book_condition, shelf_location, int(shelf_row))
                        st.session_state.success_message = f"Book '{title}' updated successfully!"
                        st.rerun()
        else:
            st.info("There are no books in the library to edit.")

    elif mode == "🗑️ Delete Book":
        st.subheader("Delete an Existing Book")
        all_books = Read.read_all_books()
    
        if not all_books.empty:
            options = all_books.apply(lambda row: f"{row['Title']} (ISBN: {row['ISBN']})", axis=1).tolist()
            
            # When a selection is made, store it in session state
            def on_book_select():
                display = st.session_state.delete_book_select
                if display:
                    book = all_books[all_books.apply(lambda r: f"{r['Title']} (ISBN: {r['ISBN']})", axis=1) == display].iloc[0]
                    st.session_state.book_to_delete = book
                else:
                    st.session_state.book_to_delete = None
    
            st.selectbox(
                "Select a book to delete",
                options=options,
                index=None,
                placeholder="Search or select a book from the list...",
                key="delete_book_select", # Use a key to track selection
                on_change=on_book_select # Callback to save the selected book
            )
    
            # The rest of the logic now reads from session state
            if "book_to_delete" in st.session_state and st.session_state.book_to_delete is not None:
                selected_book = st.session_state.book_to_delete
                st.warning(f"Are you sure you want to delete **{selected_book['Title']}** by {selected_book['Author']}?")
                
                def delete_book_callback():
                    # The callback also reads from session state
                    book_to_delete = st.session_state.book_to_delete
                    Write.delete_book(book_to_delete["ISBN"])
                    st.session_state.success_message = f"Book '{book_to_delete['Title']}' deleted successfully!"
                    # Clean up session state
                    del st.session_state.book_to_delete
                    del st.session_state.delete_book_select
    
                with st.form("delete_book_form"):
                    st.form_submit_button(
                        "🗑️ Yes, Delete This Book",
                        on_click=delete_book_callback,
                        type="primary"
                    )
        else:
            st.info("There are no books in the library to delete.")

# === SEARCH BOOKS ===
elif selection == "🔎 Search Books":
    st.subheader("Search the Library Catalog")
    all_books_df = Read.read_books()
    
    if all_books_df.empty:
        st.info("No books in the library to search.")
    else:
        # --- Create All Filter Widgets First ---

        # 1. Main searchable dropdown is now at the top
        all_books_df['display'] = all_books_df['Title'] + ' (ISBN: ' + all_books_df['ISBN'] + ')'
        options = [f"Show All ({len(all_books_df)} books)"] + all_books_df['display'].tolist()
        selected_book_display = st.selectbox(
            "🔍 Search for a specific book by Title or ISBN",
            options=options
        )

        # 2. Secondary filters are below
        col1, col2 = st.columns(2)
        with col1:
            filter_genres = ["All"] + sorted(all_books_df["Genre"].unique())
            selected_genre = st.selectbox("🔽 Filter by Genre", filter_genres)
        with col2:
            view_mode = st.radio("Filter by Status", ["All Books", "Available", "Borrowed"], horizontal=True)

        st.markdown("---")

        # --- Apply All Filters Sequentially ---
        display_df = all_books_df.copy()

        # Apply main search filter
        if not selected_book_display.startswith("Show All"):
            display_df = display_df[display_df['display'] == selected_book_display]
        
        # Apply genre filter
        if selected_genre != "All":
            display_df = display_df[display_df["Genre"] == selected_genre]
        
        # Apply status filter
        if view_mode == "Available":
            display_df = display_df[display_df["IsInStock"] == 1]
        elif view_mode == "Borrowed":
            display_df = display_df[display_df["IsInStock"] == 0]

        # --- Display the final table ---
        if not display_df.empty:
            display_df["In Stock"] = display_df["IsInStock"].map({1: "Yes", 0: "No"})
            cols_to_display = ["ISBN", "Title", "Author", "Genre", "Condition", "In Stock", "Location"]
            st.dataframe(
                display_df[cols_to_display],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No books match your search and filter criteria.")