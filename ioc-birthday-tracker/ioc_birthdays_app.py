import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="IOC Birthday Tracker", layout="wide")

# Load CSV safely
csv_path = os.path.join(os.path.dirname(__file__), "ioc_members_detailed.csv")
df = pd.read_csv(csv_path)

# Convert born column to datetime
df["born_dt"] = pd.to_datetime(df["born"], format="%d-%b-%y", errors="coerce")
df["born_display"] = df["born_dt"].dt.strftime("%d %b")  # e.g., 31 Mar
df["born_sort"] = df["born_dt"].dt.strftime("%m-%d")

# Today's date
today = datetime.today()
today_day = today.day
today_month = today.month

# Header
st.markdown("## 🎂 IOC위원 생일 알리미")
st.markdown(f"오늘 날짜: {today.strftime('%Y-%m-%d')}")

st.markdown("---")

# -------------------- 오늘 생일 --------------------
st.markdown("### 🎉 오늘 생일인 위원")


todays_birthdays = df[
    (df["born_dt"].dt.day == today_day) & (df["born_dt"].dt.month == today_month)
]

def display_card(row, image_size=100):
    st.markdown(f"""
        <div style='display:flex; align-items:center; padding:10px 0;'>
            <img src="{row['mugshot_url']}" style='border-radius:8px; width:{image_size}px; margin-right:20px;'>
            <div>
                <p style='margin:0'><strong>{row['classification']}</strong></p>
                <p style='margin:0'><a href="{row['profile_url']}" target="_blank" style='color:#1f77b4;'>{row['name']}</a></p>
                <p style='margin:0; color:gray;'>🎂 {row['born_display']}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

if not todays_birthdays.empty:
    for _, row in todays_birthdays.iterrows():
        display_card(row)
else:
    st.markdown("🕊 오늘은 생일인 IOC 위원이 없습니다.")

# -------------------- 다가오는 생일 --------------------
st.markdown("### 🔜 다가오는 생일 (15일 이내)")

next_15_days = [(today + timedelta(days=i)).strftime("%m-%d") for i in range(1, 16)]
df["mmdd"] = df["born_dt"].dt.strftime("%m-%d")
upcoming_birthdays = df[df["mmdd"].isin(next_15_days)]

with st.expander("🎈 다가오는 생일 보기"):
    if not upcoming_birthdays.empty:
        for _, row in upcoming_birthdays.sort_values("mmdd").iterrows():
            display_card(row, image_size=80)
    else:
        st.write("향후 15일 이내 생일인 IOC 위원이 없습니다.")

# -------------------- 전체 명단 --------------------

# 표에 표시할 컬럼 준비
display_df = df[[
    "name", "profile_url", "classification", "born_display", "born_sort", "entry_in_ioc", "games_participated"
]].copy()

# 컬럼명 변경
display_df.rename(columns={
    "name": "이름",
    "classification": "Member Type",
    "born_display": "Birthday",
    "entry_in_ioc": "Entry in IOC",
    "games_participated": "Games Participated",
    "profile_url": "Profile URL"
}, inplace=True)

# 검색 필터
search_query = st.text_input("🔎 이름으로 검색")
if search_query:
    display_df = display_df[display_df["이름"].str.contains(search_query, case=False, na=False)]

# 🔗 링크 버튼 추가
display_df["🔗 Profile"] = display_df["Profile URL"].apply(
    lambda url: f"[Link]({url})" if pd.notna(url) else ""
)

# 정렬용 보조 컬럼 제거
display_df.drop(columns=["born_sort", "Profile URL"], inplace=True)

# 출력
st.markdown("### 📋 전체 IOC 위원 명단")
st.caption("📅 최신화 날짜: 2025년 7월")
st.caption("💡 열 제목을 클릭해 정렬하거나, 이름으로 검색할 수 있어요.")

st.dataframe(display_df, use_container_width=True, height=500)
