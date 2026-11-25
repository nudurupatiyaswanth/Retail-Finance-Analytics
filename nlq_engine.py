import re


def generate_sql(question):

    question = question.lower().strip()

    # 1. Total Customers
    if any(word in question for word in [
        "total customers",
        "number of customers",
        "how many customers"
    ]):
        return {
            "sql": """
                SELECT COUNT(*) AS total_customers
                FROM customers
            """,
            "params": (),
            "explanation": "Counts the total number of customers."
        }

    # 2. Show All Customers
    elif "customer" in question and any(
        word in question for word in ["show", "list", "display", "all"]
    ):
        return {
            "sql": """
                SELECT customer_id, customer_name, email,
                       city, state, credit_score
                FROM customers
                ORDER BY customer_id
            """,
            "params": (),
            "explanation": "Displays customer information."
        }

    # 3. Total Transaction Amount
    elif "transaction" in question and any(
        word in question for word in ["amount", "sum", "value"]
    ):
        return {
            "sql": """
                SELECT COALESCE(SUM(amount), 0)
                AS total_transaction_amount
                FROM transactions
            """,
            "params": (),
            "explanation": "Calculates the total transaction amount."
        }

    # 4. Total Transactions
    elif any(word in question for word in [
        "total transactions",
        "number of transactions",
        "how many transactions"
    ]):
        return {
            "sql": """
                SELECT COUNT(*) AS total_transactions
                FROM transactions
            """,
            "params": (),
            "explanation": "Counts all transactions."
        }

    # 5. Recent Transactions
    elif "transaction" in question and any(
        word in question for word in ["recent", "latest"]
    ):
        return {
            "sql": """
                SELECT transaction_id, customer_id,
                       transaction_date, transaction_type,
                       amount, status
                FROM transactions
                ORDER BY transaction_date DESC
                LIMIT 10
            """,
            "params": (),
            "explanation": "Displays the 10 most recent transactions."
        }

    # 6. Payment Status Analysis
    elif "payment" in question and any(
        word in question for word in ["status", "analysis", "breakdown", "distribution"]
    ):
        return {
            "sql": """
                SELECT payment_status, COUNT(*) AS total
                FROM payments
                GROUP BY payment_status
                ORDER BY total DESC
            """,
            "params": (),
            "explanation": "Groups payments according to their status."
        }

    # 7. Loan Status Analysis
    elif "loan" in question and any(
        word in question for word in ["status", "analysis", "breakdown", "distribution"]
    ):
        return {
            "sql": """
                SELECT loan_status, COUNT(*) AS total
                FROM loans
                GROUP BY loan_status
                ORDER BY total DESC
            """,
            "params": (),
            "explanation": "Groups loans according to their status."
        }

    # 8. Overdue Loans
    elif "overdue" in question and "loan" in question:
        return {
            "sql": """
                SELECT loan_id, customer_id, loan_amount,
                       due_date, outstanding_amount
                FROM loans
                WHERE loan_status = %s
                ORDER BY due_date
            """,
            "params": ("Overdue",),
            "explanation": "Displays all overdue loans."
        }

    # 9. Show All Loans
    elif "loan" in question and any(
        word in question for word in ["show", "list", "display", "all"]
    ):
        return {
            "sql": """
                SELECT loan_id, customer_id, loan_amount,
                       interest_rate, due_date, loan_status,
                       outstanding_amount
                FROM loans
                ORDER BY loan_id
            """,
            "params": (),
            "explanation": "Displays loan information."
        }

    # 10. Show All Payments
    elif "payment" in question and any(
        word in question for word in ["show", "list", "display", "all"]
    ):
        return {
            "sql": """
                SELECT payment_id, customer_id, payment_date,
                       amount, payment_status, payment_method
                FROM payments
                ORDER BY payment_date DESC
            """,
            "params": (),
            "explanation": "Displays payment information."
        }

    # Unsupported Question
    else:
        return None