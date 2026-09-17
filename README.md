# java-squad
Backend: 
python -m uvicorn backend.api:app --reload --port 8000



Front:
export BACKEND_URL=http://127.0.0.1:8000 
streamlit run backend/Streamlit/app.py
