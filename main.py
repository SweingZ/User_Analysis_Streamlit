import streamlit as st
from datetime import datetime
import motor.motor_asyncio
import asyncio
from bson import ObjectId
import pandas as pd
from collections import Counter
import plotly.express as px  # Use Plotly Express for a simple pie chart

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
        user["_id"] = str(user["_id"])
        users.append(user)
    return users

# Function to fetch all session data
async def fetch_all_sessions():
    sessions = []
    async for session in session_collection.find():
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
        paths = session.get('path_history', [])
        if paths:
            page_views.update(paths)
    df = pd.DataFrame(list(page_views.items()), columns=['Path', 'Views'])
    df = df.sort_values('Views', ascending=False)
    return df

# Fetch and display data using Streamlit's asyncio support
def run():
    user_data, session_data = asyncio.run(fetch_data())
    
    st.sidebar.title("Filters")
    st.sidebar.write("Use the filters to narrow down your analytics view.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Total Visitors")
        st.metric("Visitors", len(user_data))  

    with col2:
        st.subheader("Total Visits")
        st.metric("Visits", len(session_data))

    st.subheader("Average Session Time")
    total_duration = 0
    bounce = 0

    for session in session_data:
        if session.get("bounce"):
            bounce += 1
        session_start = session["session_start"]
        session_end = session["session_end"]
        session_duration = session_end - session_start
        total_duration += session_duration.total_seconds()

    if len(session_data) > 0:
        average_duration = total_duration / len(session_data)
        avg_minutes, avg_seconds = divmod(average_duration, 60)
        avg_hours, avg_minutes = divmod(avg_minutes, 60)
        st.write(f"**Average Session Time:** {int(avg_hours)} hours, {int(avg_minutes)} minutes, {int(avg_seconds)} seconds")
    else:
        st.write("No session data available.")

    st.divider()

    st.subheader("Page Views Analysis")
    page_views_df = calculate_page_views(session_data)
    st.write("Page Views Chart")
    st.bar_chart(data=page_views_df.set_index('Path')['Views'])

    st.divider()

    st.subheader("Individual Page Analysis")
    if not page_views_df.empty:
        most_viewed = page_views_df.iloc[0]
        st.write(f"**Most Viewed Page:** {most_viewed['Path']} ({most_viewed['Views']} views)")
        total_views = page_views_df['Views'].sum()
        page_views_df['Percentage'] = (page_views_df['Views'] / total_views * 100).round(2)
        st.write("**Page View Distribution**")
        st.dataframe(page_views_df.assign(
            Percentage=lambda x: x['Percentage'].map('{:.2f}%'.format)
        ), use_container_width=True)

    st.divider()

    st.subheader("Bounce Rate Analysis")

    # Calculating the bounce rate percentage
    bounce_rate_percent = bounce/len(session_data) * 100
    st.write(f"**Bounce Rate Percentage:** {bounce_rate_percent:.2f}%")
    if len(session_data) > 0:
        non_bounce = len(session_data) - bounce
        bounce_data = pd.DataFrame({
            "Category": ["Bounced", "Non-Bounced"],
            "Count": [bounce, non_bounce]
        })

        # Create a donut chart by adding the hole parameter
        fig = px.pie(bounce_data, values='Count', names='Category', title="Bounce Rate Distribution", hole=0.4)
        
        # Optional: Customize colors and display percentage inside
        fig.update_traces(textinfo='percent+label')
        
        st.plotly_chart(fig)

# Run the code
run()
