import streamlit as st
import pandas as pd
import Read
import Write
import library_connection

# --- Page Setup (MUST BE FIRST) ---
st.set_page_config(layout="wide", page_title="Friends")

# --- Check Connection Status ---
if st.session_state.get("db_status") != "Connected":
    st.info("You have been disconnected. Redirecting to login page...")
    st.switch_page("Login.py")

# --- Sidebar ---
st.sidebar.button("Disconnect", on_click=library_connection.disconnect_db)

# --- Flash Message ---
if "success_message" in st.session_state:
    st.success(st.session_state.pop("success_message"))

st.title("Manage Friends")

# --- NAVIGATION ---
# ✅ Replaced st.tabs with a stateful st.radio widget
selection = st.radio(
    "Friends Navigation",
    ["📋 View All", "➕ Add Friend", "✏️ Update Friend", "❌ Delete Friend"],
    key="friends_nav",
    horizontal=True,
    label_visibility="collapsed"
)

# === View All ===
if selection == "📋 View All":
    st.subheader("All Friends")
    all_friends_df = Read.get_friends() 

    if all_friends_df.empty:
        st.info("No friends found.")
    else:
        # Create a list of options for the searchable dropdown, with "Show All" as the default
        friend_options = ["Show All"] + all_friends_df['display'].tolist()
        
        selected_friend_display = st.selectbox(
            "Search for a friend by typing their name or ID",
            options=friend_options
        )

        # Filter the DataFrame based on the selection
        if selected_friend_display == "Show All":
            display_df = all_friends_df
        else:
            display_df = all_friends_df[all_friends_df['display'] == selected_friend_display]
        
        # Display the main table (either full or filtered)
        st.dataframe(display_df[['FriendID', 'FName', 'LName', 'MaxLoans']], use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Get Contact Information")
        
        # Only show contact info if a specific friend is selected
        if selected_friend_display != "Show All":
            selected_friend_id = display_df['FriendID'].iloc[0]
            contact_df = Read.get_friend_contact_info(friend_id=selected_friend_id)
            if not contact_df.empty:
                st.write(f"**Contact Details for {selected_friend_display}:**")
                cols = st.columns(len(contact_df))
                for idx, col in enumerate(cols):
                    contact_type = contact_df.iloc[idx]['type']
                    contact_value = contact_df.iloc[idx]['contact']
                    col.metric(label=contact_type.capitalize(), value=contact_value)
            else:
                st.warning("No contact information found for this friend.")
        else:
            st.info("Select a specific friend from the dropdown above to see their contact details.")
            
# === Add Friend ===
elif selection == "➕ Add Friend":
    st.subheader("➕ Add a New Friend")
    
    # --- Initialize State for the form ---
    if 'new_contacts' not in st.session_state:
        st.session_state.new_contacts = [{"type": "", "contact": ""}]
    if 'add_fname' not in st.session_state:
        st.session_state.add_fname = ""
    if 'add_lname' not in st.session_state:
        st.session_state.add_lname = ""
    if 'add_maxloans' not in st.session_state:
        st.session_state.add_maxloans = 2 # ✅ Set the default here

    # --- Define the callback to reset ALL form fields ---
    def reset_add_friend_form():
        st.session_state.new_contacts = [{"type": "", "contact": ""}]
        st.session_state.add_fname = ""
        st.session_state.add_lname = ""
        st.session_state.add_maxloans = 2 # ✅ And also reset to it here
        if "add_type_0" in st.session_state:
            st.session_state.add_type_0 = ""
        if "add_contact_0" in st.session_state:
            st.session_state.add_contact_0 = ""

    def add_contact_row():
        st.session_state.new_contacts.append({"type": "", "contact": ""})
    
    def submit_add_friend():
        # ... (your existing submit logic)
        final_contacts = []
        for i in range(len(st.session_state.new_contacts)):
            contact_type = st.session_state.get(f"add_type_{i}", "")
            contact_info = st.session_state.get(f"add_contact_{i}", "")
            final_contacts.append({"type": contact_type, "contact": contact_info})
        if not (st.session_state.add_fname and st.session_state.add_lname):
            st.warning("First and Last Name are required.")
        else:
            if Write.add_friend_with_contacts(st.session_state.add_fname, st.session_state.add_lname, st.session_state.add_maxloans, final_contacts):
                st.session_state.success_message = "Friend added successfully!"
                reset_add_friend_form() 
                st.cache_data.clear()

    # --- Action Buttons ---
    col1, col2 = st.columns(2)
    with col1:
        st.button("Add additional contact information", on_click=add_contact_row, use_container_width=True)
    with col2:
        st.button("Reset Form", on_click=reset_add_friend_form, use_container_width=True)

    st.markdown("---")

    # --- Final Submission Form ---
    with st.form("add_friend_form"):
        st.write("**Friend's Details**")
        c1, c2 = st.columns(2)
        st.text_input("First Name", key="add_fname")
        st.text_input("Last Name", key="add_lname")
        # The value is now controlled by the key, which defaults to 2
        st.number_input("Max Loans", min_value=0, step=1, key="add_maxloans")
        
        st.markdown("---")
        st.write("**Contact Information**")
        
        for i in range(len(st.session_state.new_contacts)):
            c1, c2 = st.columns(2)
            c1.text_input("Contact Type", key=f"add_type_{i}")
            c2.text_input("Contact Info", key=f"add_contact_{i}")
        
        st.form_submit_button("💾  Save Friend", on_click=submit_add_friend)

# === Update Friend ===
elif selection == "✏️ Update Friend":
    st.subheader("Update Friend Information")
    all_friends_df = Read.get_friends()
    if all_friends_df.empty:
        st.info("No friends available to update.")
    else:
        selected_friend_display = st.selectbox("Select a friend to update", options=all_friends_df['display'].tolist(), index=None)
        if selected_friend_display:
            selected_friend_id = all_friends_df[all_friends_df['display'] == selected_friend_display]['FriendID'].iloc[0]
            selected_friend_data = all_friends_df[all_friends_df['FriendID'] == selected_friend_id].iloc[0]

            with st.form("update_friend_form"):
                st.write(f"Editing: **{selected_friend_display}**")
                FName = st.text_input("First Name", value=selected_friend_data['FName'])
                LName = st.text_input("Last Name", value=selected_friend_data['LName'])
                MaxLoans = st.number_input("Max Loans", value=selected_friend_data['MaxLoans'], step=1)
                if st.form_submit_button("Update Friend Details"):
                    if Write.update_friend(selected_friend_id, FName, LName, MaxLoans):
                        st.session_state.success_message = "Friend details updated successfully!"
                        st.cache_data.clear()
                        st.rerun()
            
            st.markdown("---")
            st.write("**Manage Contacts**")
            contact_df = Read.get_friend_contact_info(friend_id=selected_friend_id)
            if not contact_df.empty:
                for index, row in contact_df.iterrows():
                    c1, c2, c3 = st.columns([2, 3, 1])
                    c1.write(f"**{row['type'].capitalize()}:**")
                    c2.write(row['contact'])
                    if c3.button("Delete", key=f"del_contact_{row['ContactID']}"):
                        Write.delete_contact(row['ContactID'])
                        st.session_state.success_message = "Contact deleted."
                        st.cache_data.clear()
                        st.rerun()
            else:
                st.info("No contacts found for this friend.")

            with st.form("add_contact_form", clear_on_submit=True):
                st.write("**Add New Contact**")
                c1, c2 = st.columns(2)
                contact_type = c1.text_input("Contact Type")
                contact_info = c2.text_input("Contact Info")
                if st.form_submit_button("Add Contact"):
                    if contact_type and contact_info:
                        Write.add_contact_to_friend(selected_friend_id, contact_type, contact_info)
                        st.session_state.success_message = "Contact added."
                        st.cache_data.clear()
                        st.rerun()

# === Delete Friend ===
elif selection == "❌ Delete Friend":
    st.subheader("Delete a Friend")
    all_friends_df = Read.get_friends()
    if all_friends_df.empty:
        st.info("No friends available to delete.")
    else:
        selected_friend_display = st.selectbox("Select a friend to delete", options=all_friends_df['display'].tolist(), index=None)
        if selected_friend_display:
            selected_friend_id = all_friends_df[all_friends_df['display'] == selected_friend_display]['FriendID'].iloc[0]
            st.warning(f"Are you sure you want to delete **{selected_friend_display}**? This will also delete all their loans and cannot be undone.")
            def delete_friend_callback():
                Write.delete_friend(selected_friend_id)
                st.session_state.success_message = "Friend deleted successfully!"
                st.cache_data.clear()
            with st.form("delete_friend_form"):
                st.form_submit_button("Confirm Delete", on_click=delete_friend_callback, type="primary")