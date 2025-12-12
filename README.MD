# Tweet Sentiment (snscrape + VADER + Streamlit)

Local run:
1. python3 -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. python3 poller/snspoller.py   # start poller (creates tweets.db)
5. streamlit run dashboard/dashboard.py --server.port 8501 --server.address 0.0.0.0