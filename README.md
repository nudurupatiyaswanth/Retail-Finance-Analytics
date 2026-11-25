# Retail Finance NL2SQL Dashboard

## Included
- Flask backend and existing API routes
- Existing natural-language-to-SQL engine
- Refreshed responsive dashboard UI
- Query results rendered as text-safe table cells

## Setup
1. Install Python 3.10+.
2. Create and activate a virtual environment.
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env`.
5. Fill in your own MySQL connection details in `.env`.
6. Ensure the MySQL database and the expected tables (`customers`, `transactions`, `payments`, `loans`) exist.
7. Start the application: `python app.py`
8. Open `http://127.0.0.1:5001` in your browser.

The dashboard uses the existing API endpoints:
`/api/summary`, `/api/payment-analysis`, `/api/loan-analysis`, and `/api/ask`.

## Security
The real `.env` file and virtual environment are intentionally excluded from this ZIP.
Never share `.env` or commit it to Git.
