# Lion Agent Frontend

## Setup

pip install -r requirements.txt

## Run

export BACKEND_URL=http://localhost:8000
streamlit run app.py

## Backend Format

POST /ask
{
  "question": "string"
}
