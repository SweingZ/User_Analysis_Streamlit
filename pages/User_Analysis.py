import streamlit as st

# Retrieve user data and session data from session state
user_data = st.session_state.get("user_data", []) 
session_data = st.session_state.get("session_data", [])  

if not user_data or not session_data:
    st.warning("No user or session data available.")
    st.stop()

st.title("User Analysis")

# Extract user names from the list of dictionaries
st.sidebar.header("Users")
users = [user["name"] for user in user_data]

# Allow user selection
selected_user_name = st.sidebar.selectbox("Select a User", users)

if selected_user_name:
    st.subheader(f"Session History for {selected_user_name}")

    # Retrieve the selected user's data
    selected_user = next(user for user in user_data if user["name"] == selected_user_name)

    # Extract session IDs for the selected user
    session_ids = [str(session_id) for session_id in selected_user.get("session_ids", [])]

    # Adjust the filtering based on session_data structure
    sessions = [session for session in session_data if session.get("_id") in session_ids]

    if not sessions:
        st.info("No sessions available for this user.")
    else:
        for idx, session in enumerate(sessions, 1):
            # Create an expandable section for each session
            with st.expander(f"Session {idx} Details"):
                st.write(f"**Session Start:** {session.get('session_start', {})}")
                st.write(f"**Session End:** {session.get('session_end', {})}")
                st.write("**Path History:**")
                st.write(session.get("path_history", []))

                # Additional details if needed
                if session.get("bounce"):
                    st.warning("This session resulted in a bounce.")

# Optional feature: Add a button to download user session history as a CSV
if st.button("Download User Sessions as CSV"):
    import pandas as pd

    # Flatten session data for export
    flattened_sessions = []
    for session in sessions:
        flattened_sessions.append({
            "Session Start": session.get("session_start", {}).get("$date"),
            "Session End": session.get("session_end", {}).get("$date"),
            "Path History": ",".join(session.get("path_history", [])),
            "Bounce": session.get("bounce", False)
        })

    # Convert to DataFrame and download as CSV
    df = pd.DataFrame(flattened_sessions)
    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"{selected_user_name}_sessions.csv",
        mime="text/csv"
    )
