# Real-Time Twitter Sentiment Dashboard (Polling)
### By **John Joshua**

A real-time streaming dashboard that tracks live tweets related to:

- `python`
- `aws`
- `cloud`
- `data`
- `ai`

Tweets are fetched using the **Twitter API**, analyzed for **sentiment**, stored in a local SQLite database, and visualized instantly using **Streamlit**.

This project demonstrates skills in **APIs, data engineering, automation, NLP sentiment analysis, and dashboard development**.

---

# 🚀 Features

### ✅ Real-time Tweet Polling  
Fetches new tweets every 60 seconds using your **Twitter Bearer Token**.

### ✅ Sentiment Analysis  
Each tweet is labeled as:
- **Positive**
- **Neutral**
- **Negative**

### ✅ Interactive Streamlit Dashboard  
Includes:
- Live tweets table  
- Sentiment distribution bar chart  
- Sentiment trend line chart  
- Word cloud of frequent words  
- Auto-refresh for real-time updates  

### ✅ Local Database Storage  
- Uses **SQLite (`tweets.db`)**  
- Prevents duplicate insertion  
- Stores tweet text, timestamp, sentiment score, and label  

### ✅ Secure Credentials  
- `.env` keeps API secrets private  
- `.gitignore` ensures your token & database stay out of GitHub  

---

# 🧠 Architecture Overview


### 1. Poller (`snspoller.py`)
- Polls Twitter API  
- Filters by given keywords  
- Stores parsed tweets into SQLite  
- Performs sentiment scoring  

### 2. Database  
- Lightweight **SQLite** for fast storage  
- Easy portability & deployment  

### 3. Dashboard (`dashboard.py`)
- Shows analysis in real-time  
- Uses Streamlit for interactive visuals  

---

# 🛠 Tech Stack

| Component | Technology |
|----------|------------|
| Language | Python |
| API | Twitter API v2 (Bearer Token) |
| Polling | Tweepy |
| NLP | TextBlob |
| DB | SQLite |
| UI | Streamlit |
| Env Mgmt | Virtualenv |
| Deployment | AWS EC2 |

---

# 📂 Project Structure


---

# 🔐 Environment Variables

Create `.env` file in root folder:


Ensure `.gitignore` contains:


---

# ⚙️ Installation (Local Machine)

### 1. Clone the repository

### 2. Create a virtual environment  

### 3. Activate it  
**Windows**

### 4. Install dependencies  

### 5. Add `.env` with your Bearer Token  

### 6. Run the tweet poller  


### 7. Run the dashboard  

---

# 🌩 Deploying on AWS EC2 (Simple Guide)

### 1. Launch EC2 Ubuntu instance  
- Choose **t2.micro (free tier)**  
- Region: **us-east-1** recommended  
- Allow ports:
  - 22 (SSH)
  - 8501 (Streamlit dashboard)

### 2. SSH into EC2  

### 3. Install Python & Git  

### 4. Clone your GitHub repo  

### 5. Create venv & install packages  

### 6. Add your `.env` on EC2  

### 8. Run Streamlit publicly  

### 9. Visit your dashboard  

---

# 🧩 Future Improvements  
- Move database to PostgreSQL (RDS)  
- Add Docker support  
- Add login/authentication  
- Deploy using AWS Elastic Beanstalk  
- Use ML transformer models for sentiment  

---

# 🏁 Final Notes

This project shows real, practical skills in:
- API integration  
- Automation loops  
- Real-time data processing  
- NLP sentiment analysis  
- Database design  
- Dashboard UI  
- Deployment-ready coding  

Perfect for showcasing as a **BCA 2024 graduate project**, especially with a career gap — shows dedication, technical ability, and initiative.




