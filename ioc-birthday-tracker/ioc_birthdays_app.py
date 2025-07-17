import streamlit as st
import pandas as pd
from datetime import datetime

# Load CSV
df = pd.read_csv("ioc_members_detailed.csv")

# Convert born column to datetime
df["born_dt"] = pd.to_datetime(df["born"], format="%d-%b-%y", errors="coerce")

# Add display-friendly and sortable birthday columns
df["born_display"] = df["born_dt"].dt.strftime("%d %b")  # e.g., 31 Mar
df["born_sort"] = df["born_dt"].dt.strftime("%m-%d")     # e.g., 03-31

# Today's date
today = datetime.today()
today_day = today.day
today_month = today.month

# Filter today's birthdays
todays_birthdays = df[
    (df["born_dt"].dt.day == today_day) &
    (df["born_dt"].dt.month == today_month)
]

# App title
st.title("IOC 위원 생일 알리미")
st.markdown("## 🎉 오늘 생일인 IOC위원")

# Function to show today's birthdays
def display_member_row(row):
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(row["mugshot_url"], width=100)
    with col2:
        st.markdown(f"**Member Type:** {row['classification']}")
        st.markdown(f"**Name:** [{row['name']}]({row['profile_url']})")
        st.markdown(f"**Birthday:** {row['born_display'] or '—'}")
    st.markdown("---")

if not todays_birthdays.empty:
    for _, row in todays_birthdays.iterrows():
        display_member_row(row)
else:
    st.markdown("🕊 오늘은 생일인 IOC위원이 없습니다. ")

# --- Upcoming Birthdays (Next 15 days) ---
from datetime import timedelta

st.markdown("## 🔜 다가오는 생일")

# Calculate the next 15 days
next_15_days = [(today + timedelta(days=i)).strftime("%m-%d") for i in range(1, 16)]

# Filter members whose birthday falls in the next 15 days (ignoring year)
df["mmdd"] = df["born_dt"].dt.strftime("%m-%d")
upcoming_birthdays = df[df["mmdd"].isin(next_15_days)]

with st.expander("🎈 향후 15일 이내 생일인 IOC위원 보기"):
    if not upcoming_birthdays.empty:
        for _, row in upcoming_birthdays.sort_values("mmdd").iterrows():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(row["mugshot_url"], width=80)
            with col2:
                st.markdown(f"**Member Type:** {row['classification']}")
                st.markdown(f"**Name:** [{row['name']}]({row['profile_url']})")
                st.markdown(f"**Birthday:** {row['born_display']}")
            st.markdown("---")
    else:
        st.write("향후 15일 이내 생일인 IOC위원이 없습니다. ")

# Section: Full List
st.markdown("## 📋 IOC위원 명단")
st.caption("Updated: July 2025 / 열 제목을 클릭해서 정렬하세요")

# Search bar
search_query = st.text_input("🔎 이름으로 검색")

# Create a DataFrame for display
display_df = df[[
    "name", "classification", "born_display", "born_sort", "entry_in_ioc", "games_participated"
]].copy()

# Rename columns for user-friendly display
display_df.rename(columns={
    "name": "Name",
    "classification": "Member Type",
    "born_display": "Birthday",
    "entry_in_ioc": "Entry in IOC",
    "games_participated": "Games Participated"
}, inplace=True)

# Sort by birthday if user clicks the column (now possible)
display_df = display_df.sort_values(by="born_sort")

# Drop the sort helper column from view
display_df.drop(columns=["born_sort"], inplace=True)

# Filter by name if search query exists
if search_query:
    display_df = display_df[display_df["Name"].str.contains(search_query, case=False, na=False)]

# Display the table
st.dataframe(display_df[["Name", "Member Type", "Birthday", "Entry in IOC", "Games Participated"]], use_container_width=True)

