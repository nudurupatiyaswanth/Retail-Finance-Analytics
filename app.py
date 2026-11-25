from flask import Flask, jsonify, render_template, request, Response
import mysql.connector
from dotenv import load_dotenv
import os
from nlq_engine import generate_sql
import csv
from io import StringIO


load_dotenv()

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", "3306"))
    )

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/summary")
def summary():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_customers FROM customers")
    customers = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) AS total_transactions FROM transactions")
    transactions = cursor.fetchone()

    cursor.execute("SELECT SUM(amount) AS total_transaction_amount FROM transactions")
    amount = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify({
        "total_customers": customers["total_customers"],
        "total_transactions": transactions["total_transactions"],
        "total_transaction_amount": float(amount["total_transaction_amount"] or 0)
    })

@app.route("/api/payment-analysis")
def payment_analysis():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT payment_status, COUNT(*) AS total
        FROM payments
        GROUP BY payment_status
    """)

    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(data)


@app.route("/api/loan-analysis")
def loan_analysis():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT loan_status, COUNT(*) AS total
        FROM loans
        GROUP BY loan_status
    """)

    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(data)
@app.route("/api/ask", methods=["POST"])
def ask_question():

    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Please enter a question"}), 400

    generated = generate_sql(question)

    if not generated:
        return jsonify({
            "error": "Sorry, I cannot understand this question."
        }), 400

    conn = None
    cursor = None

    try:
        sql = generated["sql"]
        params = generated.get("params", ())

        if not sql.strip().upper().startswith("SELECT"):
            return jsonify({"error": "Only SELECT queries are allowed"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(sql, params)
        results = cursor.fetchall()

        return jsonify({
            "question": question,
            "sql": sql,
            "explanation": generated.get("explanation", ""),
            "results": results,
            "total_rows": len(results)
        })

    except Exception:
        app.logger.exception("Natural language query failed")
        return jsonify({"error": "Database query failed"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            # Get all transactions
@app.route("/api/transactions")
def get_transactions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT transaction_id, customer_id,
                   transaction_date, transaction_type,
                   amount, status
            FROM transactions
            ORDER BY transaction_date DESC
        """)

        return jsonify(cursor.fetchall())

    finally:
        cursor.close()
        conn.close()


# Get all payments
@app.route("/api/payments")
def get_payments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT payment_id, customer_id,
                   payment_date, amount,
                   payment_status, payment_method
            FROM payments
            ORDER BY payment_date DESC
        """)

        return jsonify(cursor.fetchall())

    finally:
        cursor.close()
        conn.close()


# Get all loans
@app.route("/api/loans")
def get_loans():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT loan_id, customer_id, loan_amount,
                   interest_rate, due_date,
                   loan_status, outstanding_amount
            FROM loans
            ORDER BY due_date
        """)

        return jsonify(cursor.fetchall())

    finally:
        cursor.close()
        conn.close()
        # CSV REPORT DOWNLOAD
@app.route("/api/export/<report_type>")
def export_csv(report_type):

    allowed_tables = {
        "transactions": {
            "query": """
                SELECT transaction_id, customer_id,
                       transaction_date, transaction_type,
                       amount, status
                FROM transactions
                ORDER BY transaction_date DESC
            """
        },
        "payments": {
            "query": """
                SELECT payment_id, customer_id, payment_date,
                       amount, payment_status, payment_method
                FROM payments
                ORDER BY payment_date DESC
            """
        },
        "loans": {
            "query": """
                SELECT loan_id, customer_id, loan_amount,
                       interest_rate, due_date, loan_status,
                       outstanding_amount
                FROM loans
                ORDER BY due_date
            """
        }
    }

    if report_type not in allowed_tables:
        return jsonify({"error": "Invalid report type"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(allowed_tables[report_type]["query"])
        records = cursor.fetchall()

        output = StringIO()

        if records:
            writer = csv.DictWriter(output, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)

        response = Response(
            output.getvalue(),
            mimetype="text/csv"
        )

        response.headers["Content-Disposition"] = (
            f"attachment; filename={report_type}_report.csv"
        )

        return response

    finally:
        cursor.close()
        conn.close()
        # CSV REPORT DOWNLOAD



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
