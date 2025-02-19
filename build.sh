
pip install --upgrade pip

source venv\Scripts\activate

uvicorn main:app --host 0.0.0.0 --port 10000
