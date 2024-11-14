import streamlit as st
from datetime import datetime
import motor.motor_asyncio
import asyncio
from bson import ObjectId
import pandas as pd
from collections import Counter

# Connect to MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://spandanbhattarai79:spandan123@spandan.ey3fvll.mongodb.net/")
database = client.USER_ANALYSIS
user_collection = database.user
session_collection = database.session_data

st.set_page_config(page_title="User Analytics Dashboard", layout="wide")

st.title("User Analytics Dashboard")

# Function to fetch all user data
async def fetch_all_users():
    users = []
    async for user in user_collection.find():
        # Convert ObjectId to string for JSON serialization
        user["_id"] = str(user["_id"])
        users.append(user)
    return users

# Function to fetch all session data
async def fetch_all_sessions():
    sessions = []
    async for session in session_collection.find():
        # Convert ObjectId to string for JSON serialization
        session["_id"] = str(session["_id"])
        sessions.append(session)
    return sessions

# Function to fetch both user and session data
async def fetch_data():
    user_data = await fetch_all_users()
    session_data = await fetch_all_sessions()
    return user_data, session_data

def calculate_page_views(session_data):
    page_views = Counter()
    
    for session in session_data:
        # Get path_history from the session
        paths = session.get('path_history', [])
        if paths:
            # Count each path occurrence
            page_views.update(paths)
    
    # Convert to DataFrame for better visualization
    df = pd.DataFrame(list(page_views.items()), columns=['Path', 'Views'])
    df = df.sort_values('Views', ascending=False)
    return df

# Fetch and display data using Streamlit's asyncio support
def run():
    user_data, session_data = asyncio.run(fetch_data())
    
    # Create a sidebar for additional navigation options
    st.sidebar.title("Filters")
    st.sidebar.write("Use the filters to narrow down your analytics view.")

    # Display the main dashboard layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Total Visitors")
        st.metric("Visitors", len(user_data))  # Display the total visitors as a metric

    with col2:
        st.subheader("Total Visits")
        st.metric("Visits", len(session_data))  # Display the total sessions as a metric

    st.subheader("Average Session Time")

    # Initialize the sum of session durations
    total_duration = 0

    # Loop through each session and calculate the duration
    for session in session_data:
        # Convert session_start and session_end to datetime objects if they are strings
        session_start = session["session_start"]
        session_end = session["session_end"]

        # Calculate the duration as a timedelta object
        session_duration = session_end - session_start

        # Add the session duration to the total duration
        total_duration += session_duration.total_seconds()  # Convert to seconds for consistency

    # Calculate the average session time (in seconds)
    if len(session_data) > 0:
        average_duration = total_duration / len(session_data)
        # Convert seconds back to a readable time format (HH:MM:SS)
        avg_minutes, avg_seconds = divmod(average_duration, 60)
        avg_hours, avg_minutes = divmod(avg_minutes, 60)
        st.write(f"**Average Session Time:** {int(avg_hours)} hours, {int(avg_minutes)} minutes, {int(avg_seconds)} seconds")
    else:
        st.write("No session data available.")


    # Display page views analysis
    st.subheader("Page Views Analysis")
    
    # Calculate page views
    page_views_df = calculate_page_views(session_data)
    

    st.write("Page Views Chart")
    st.bar_chart(data=page_views_df.set_index('Path')['Views'])

    # Additional Analytics
    st.subheader("Individual Page Analysis")
    
    if not page_views_df.empty:
        most_viewed = page_views_df.iloc[0]
        st.write(f"**Most Viewed Page:** {most_viewed['Path']} ({most_viewed['Views']} views)")
        
        # Calculate percentage of total views for each page
        total_views = page_views_df['Views'].sum()
        page_views_df['Percentage'] = (page_views_df['Views'] / total_views * 100).round(2)
        
        st.write("**Page View Distribution**")
        st.dataframe(page_views_df.assign(
            Percentage=lambda x: x['Percentage'].map('{:.2f}%'.format)
        ), use_container_width=True)


# Run the code
run()
