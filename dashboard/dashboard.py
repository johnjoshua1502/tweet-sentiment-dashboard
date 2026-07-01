# dashboard/dashboard.py
import streamlit as st
import pandas as pd
import sqlite3
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from textblob import TextBlob

# -------------------- Paths --------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "tweets.db")
TEXT_COLUMNS = ("text", "tweet", "tweet_text", "content", "message", "body")
USER_COLUMNS = ("username", "user", "author", "screen_name")
CREATED_COLUMNS = ("created_at", "tweet_created", "timestamp", "date", "time")
LABEL_COLUMNS = ("label", "sentiment_label", "sentiment", "polarity")
SCORE_COLUMNS = ("sentiment", "score", "polarity", "sentiment_score")
MAX_UPLOAD_BYTES = 2 * 1024 * 1024
MAX_CSV_ROWS = 5000

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


def first_existing_column(dataframe, columns):
    normalized = {column.lower().strip(): column for column in dataframe.columns}
    for column in columns:
        if column in normalized:
            return normalized[column]
    return None


def score_text(text):
    score = TextBlob(str(text)).sentiment.polarity
    if score > 0:
        label = "positive"
    elif score < 0:
        label = "negative"
    else:
        label = "neutral"
    return score, label


def load_uploaded_tweets(uploaded_file):
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise ValueError("CSV upload must be 2 MB or smaller.")

    uploaded = pd.read_csv(uploaded_file)
    if len(uploaded) > MAX_CSV_ROWS:
        raise ValueError("CSV upload must contain 5000 rows or fewer.")

    text_column = first_existing_column(uploaded, TEXT_COLUMNS)
    if text_column is None:
        raise ValueError("CSV must include a tweet or text column.")

    user_column = first_existing_column(uploaded, USER_COLUMNS)
    created_column = first_existing_column(uploaded, CREATED_COLUMNS)
    label_column = first_existing_column(uploaded, LABEL_COLUMNS)
    score_column = first_existing_column(uploaded, SCORE_COLUMNS)

    normalized = pd.DataFrame()
    normalized["text"] = uploaded[text_column].fillna("").astype(str)
    normalized = normalized[normalized["text"].str.strip() != ""]
    if normalized.empty:
        raise ValueError("CSV must include at least one non-empty tweet.")

    normalized["id"] = [f"uploaded-{index + 1}" for index in range(len(normalized))]
    normalized["username"] = (
        uploaded.loc[normalized.index, user_column].fillna("uploaded").astype(str)
        if user_column
        else "uploaded"
    )

    if created_column:
        normalized["created_at"] = pd.to_datetime(
            uploaded.loc[normalized.index, created_column], errors="coerce"
        )
    else:
        normalized["created_at"] = pd.Timestamp.utcnow()
    normalized["created_at"] = normalized["created_at"].fillna(pd.Timestamp.utcnow())
    normalized["fetched_at"] = pd.Timestamp.utcnow()

    if score_column:
        normalized["sentiment"] = pd.to_numeric(
            uploaded.loc[normalized.index, score_column], errors="coerce"
        )
    else:
        normalized["sentiment"] = pd.NA

    if label_column:
        normalized["label"] = (
            uploaded.loc[normalized.index, label_column]
            .fillna("")
            .astype(str)
            .str.lower()
        )
    else:
        normalized["label"] = ""

    scored_rows = normalized["sentiment"].isna() | ~normalized["label"].isin(
        ["positive", "neutral", "negative"]
    )
    for index in normalized[scored_rows].index:
        score, label = score_text(normalized.at[index, "text"])
        normalized.at[index, "sentiment"] = score
        normalized.at[index, "label"] = label

    return normalized.reset_index(drop=True)

# -------------------- Sidebar Filters --------------------
st.sidebar.header("Filters")
limit = st.sidebar.slider("Max recent rows", 50, 1000, 200, step=50)
data_source = st.sidebar.radio("Data Source", ["SQLite database", "Upload CSV"])

if data_source == "SQLite database":
    df = load_data(limit)
else:
    uploaded_csv = st.sidebar.file_uploader(
        "Upload tweet CSV",
        type=["csv"],
        help="Use columns such as text, tweet, username, created_at, sentiment, or label."
    )
    if uploaded_csv is None:
        st.info("Upload a CSV to inspect local tweet sentiment data.")
        st.stop()
    try:
        df = load_uploaded_tweets(uploaded_csv)
    except ValueError as error:
        st.error(str(error))
        st.stop()

if df.empty:
    if data_source == "SQLite database":
        st.info("No tweets yet. Start the poller script and wait a few loops.")
    else:
        st.info("No tweet rows were loaded from the CSV.")
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


