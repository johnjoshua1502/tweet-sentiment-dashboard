# dashboard/dashboard.py
import streamlit as st
import pandas as pd
import sqlite3
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# -------------------- Paths --------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "tweets.db")

# -------------------- Streamlit Config --------------------
st.set_page_config(
    page_title="Tweet Sentiment Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- Dark Theme Styling --------------------
st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #0e1117;
        color: #fafafa;
    }
    .sidebar .sidebar-content {
        background-color: #161b22;
        color: #fafafa;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Real-Time Tweet Sentiment Dashboard")

# -------------------- Load Data --------------------
@st.cache_data(ttl=5)
def load_data(limit=500):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM tweets ORDER BY id DESC LIMIT ?", conn, params=(limit,))
        conn.close()
        if not df.empty:
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
            df['fetched_at'] = pd.to_datetime(df['fetched_at'], errors='coerce')
        return df
    except Exception as e:
        print("DB read error:", e)
        return pd.DataFrame()

# -------------------- Sidebar Filters --------------------
st.sidebar.header("Filters")
limit = st.sidebar.slider("Max recent rows", 50, 1000, 200, step=50)

df = load_data(limit)

if df.empty:
    st.info("No tweets yet. Start the poller script and wait a few loops.")
else:
    # Keyword filter
    keywords = df['text'].str.split().explode().unique().tolist()
    keywords.insert(0, "All")
    selected_keyword = st.sidebar.selectbox("Keyword", keywords)

    # Sentiment filter
    sentiments = ["positive", "neutral", "negative"]
    selected_sentiments = st.sidebar.multiselect("Sentiment", sentiments, default=sentiments)

    # Apply filters
    filtered_df = df.copy()
    if selected_keyword != "All":
        filtered_df = filtered_df[filtered_df['text'].str.contains(selected_keyword, case=False)]
    filtered_df = filtered_df[filtered_df['label'].isin(selected_sentiments)]

    # -------------------- Latest Tweets --------------------
    st.subheader("📝 Latest Tweets")
    display_df = filtered_df.copy()
    display_df['text'] = display_df['text'].apply(lambda x: x[:100] + "..." if len(x) > 100 else x)
    st.dataframe(display_df[['fetched_at', 'created_at', 'username', 'text', 'label', 'sentiment']].head(200))

    # -------------------- Sentiment Distribution --------------------
    st.subheader("📊 Sentiment Distribution")
    counts = filtered_df['label'].value_counts().reindex(sentiments).fillna(0).astype(int)
    st.bar_chart(counts)

    # -------------------- Sentiment Trend --------------------
    st.subheader("📈 Sentiment Trend Over Time")
    if not filtered_df.empty:
        chart_df = filtered_df.sort_values(by='fetched_at')
        st.line_chart(chart_df.set_index('fetched_at')['sentiment'])

    # -------------------- WordCloud --------------------
    st.subheader("☁️ WordCloud of Tweets")
    text = " ".join(filtered_df['text'].astype(str).tolist())
    if text.strip():
        wordcloud = WordCloud(width=800, height=400, background_color="#0e1117", colormap="plasma").generate(text)
        plt.figure(figsize=(10,5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        st.pyplot(plt)
    else:
        st.info("Not enough data to generate wordcloud.")



