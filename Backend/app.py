
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "finance-tracker-secret-key")

CORS(app, supports_credentials=True)

DATABASE = "finance.db"


# Database Connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create Tables
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


init_db()


# Signup
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"message": "Please fill all fields"}), 400

    hashed_password = generate_password_hash(password)

    conn = get_db()

    try:
        conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_password)
        )

        conn.commit()

        return jsonify({"message": "Signup successful!"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"message": "Email already exists"}), 400

    finally:
        conn.close()


# Login
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        return jsonify({"message": "Login successful!"}), 200

    return jsonify({"message": "Invalid email or password"}), 401


# Logout
@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({"message": "Logout successful"}), 200


# Get Transactions
@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    if "user_id" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    conn = get_db()

    transactions = conn.execute(
        """
        SELECT * FROM transactions
        WHERE user_id = ?
        ORDER BY date DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return jsonify([dict(transaction) for transaction in transactions])


# Add Transaction
@app.route("/api/transactions", methods=["POST"])
def add_transaction():
    if "user_id" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json

    transaction_type = data.get("type")
    amount = data.get("amount")
    category = data.get("category")
    description = data.get("description")
    date = data.get("date")

    if not transaction_type or not amount or not category or not date:
        return jsonify({"message": "Please fill all required fields"}), 400

    if transaction_type not in ["income", "expense"]:
        return jsonify({"message": "Invalid transaction type"}), 400

    conn = get_db()

    conn.execute(
        """
        INSERT INTO transactions
        (user_id, type, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            transaction_type,
            amount,
            category,
            description,
            date
        )
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Transaction added successfully"}), 201


# Delete Transaction
@app.route("/api/transactions/<int:transaction_id>", methods=["DELETE"])
def delete_transaction(transaction_id):
    if "user_id" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    conn = get_db()

    conn.execute(
        """
        DELETE FROM transactions
        WHERE id = ? AND user_id = ?
        """,
        (transaction_id, session["user_id"])
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Transaction deleted successfully"}), 200


# Summary
@app.route("/api/summary", methods=["GET"])
def summary():
    if "user_id" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    conn = get_db()

    income = conn.execute(
        """
        SELECT SUM(amount) FROM transactions
        WHERE user_id = ? AND type = 'income'
        """,
        (session["user_id"],)
    ).fetchone()[0]

    expenses = conn.execute(
        """
        SELECT SUM(amount) FROM transactions
        WHERE user_id = ? AND type = 'expense'
        """,
        (session["user_id"],)
    ).fetchone()[0]

    conn.close()

    income = income or 0
    expenses = expenses or 0
    balance = income - expenses

    return jsonify({
        "income": income,
        "expenses": expenses,
        "balance": balance
    })


# Home Route
@app.route("/")
def home():
    return jsonify({"message": "Finance Tracker Backend is Running!"})


# Run Server
if __name__ == "__main__":
    app.run(debug=True, port=5000)
