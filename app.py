
from flask import Flask, request, jsonify, send_from_directory
import sqlite3

app = Flask(__name__)

DATABASE = "employees.db"


# Connect to the database
def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# Create the employee table
def initialize_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            empid TEXT NOT NULL UNIQUE,
            dob TEXT NOT NULL,
            state TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# Display the frontend application
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


# Check backend status
@app.route("/api/health")
def health():
    return jsonify({
        "status": "Backend is running"
    })


# Get all employees
@app.route("/api/employees", methods=["GET"])
def get_employees():
    connection = get_db_connection()

    employees = connection.execute(
        "SELECT * FROM employees ORDER BY id"
    ).fetchall()

    connection.close()

    return jsonify([dict(employee) for employee in employees])


# Register a new employee
@app.route("/api/employees", methods=["POST"])
def add_employee():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    empid = data.get("empid", "").strip()
    dob = data.get("dob", "").strip()
    state = data.get("state", "").strip()

    if not all([name, empid, dob, state]):
        return jsonify({
            "error": "All fields are required"
        }), 400

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO employees (name, empid, dob, state)
            VALUES (?, ?, ?, ?)
            """,
            (name, empid, dob, state)
        )

        connection.commit()

        return jsonify({
            "message": "Employee registered successfully",
            "id": cursor.lastrowid
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Employee ID already exists"
        }), 409

    finally:
        connection.close()


# Update an employee
@app.route("/api/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    empid = data.get("empid", "").strip()
    dob = data.get("dob", "").strip()
    state = data.get("state", "").strip()

    if not all([name, empid, dob, state]):
        return jsonify({
            "error": "All fields are required"
        }), 400

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE employees
            SET name = ?, empid = ?, dob = ?, state = ?
            WHERE id = ?
            """,
            (name, empid, dob, state, employee_id)
        )

        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Employee not found"
            }), 404

        return jsonify({
            "message": "Employee updated successfully"
        })

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Employee ID already exists"
        }), 409

    finally:
        connection.close()


# Delete an employee
@app.route("/api/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    connection = get_db_connection()

    cursor = connection.execute(
        "DELETE FROM employees WHERE id = ?",
        (employee_id,)
    )

    connection.commit()
    deleted = cursor.rowcount > 0
    connection.close()

    if not deleted:
        return jsonify({
            "error": "Employee not found"
        }), 404

    return jsonify({
        "message": "Employee deleted successfully"
    })


if __name__ == "__main__":
    initialize_database()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
