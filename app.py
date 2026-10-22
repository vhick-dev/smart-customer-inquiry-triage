
from flask import Flask, render_template, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "inquiries.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()



def classify_inquiry(message):
    message = message.lower().strip()

    billing_keywords = [
        "refund", "payment", "billing", "charged",
        "invoice", "transaction", "price"
    ]

    delivery_keywords = [
        "delivery", "order", "shipment", "tracking",
        "shipping", "package", "parcel"
    ]

    complaint_keywords = [
        "broken", "complaint", "damaged", "faulty",
        "defective", "not working"
    ]

    if not message:
        return "Invalid Inquiry"

    elif any(word in message for word in billing_keywords):
        return "Billing"

    elif any(word in message for word in delivery_keywords):
        return "Order or Delivery"

    elif any(word in message for word in complaint_keywords):
        return "Complaint"

    else:
        return "General Inquiry"



@app.route("/", methods=["GET", "POST"])
def home():
    category = None
    customer_message = ""

    if request.method == "POST":
        customer_message = request.form.get(
            "message", ""
        ).strip()

        if customer_message:
            category = classify_inquiry(customer_message)

            connection = get_db_connection()

            connection.execute(
                """
                INSERT INTO inquiries
                (message, category, created_at)
                VALUES (?, ?, ?)
                """,
                (
                    customer_message,
                    category,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )

            connection.commit()
            connection.close()

    return render_template(
        "index.html",
        category=category,
        customer_message=customer_message
    )



@app.route("/dashboard")
def dashboard():
    connection = get_db_connection()

    inquiries = connection.execute(
        "SELECT * FROM inquiries ORDER BY id DESC"
    ).fetchall()

    category_counts = connection.execute(
        """
        SELECT category, COUNT(*) AS total
        FROM inquiries
        GROUP BY category
        """
    ).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        inquiries=inquiries,
        category_counts=category_counts
    )



if __name__ == "__main__":
    create_table()
    app.run(debug=True)
