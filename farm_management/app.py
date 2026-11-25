import os
from flask import Flask, render_template, request, redirect
import mysql.connector
from mysql.connector import Error

# Initialize Flask app - Farm Management System (2026) by Shani
app = Flask(__name__)


def get_db_connection():
    """Create a fresh MySQL connection using env vars with existing defaults."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "shani_rajput"),
        database=os.getenv("DB_NAME", "farm_management"),
    )


# Home Page Route
@app.route("/")
def home():
    return render_template("index.html")


# Farmer Registration Route
@app.route("/farmer_register", methods=["GET", "POST"])
def farmer_register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        aadhaar = request.form.get("aadhaar", "").strip()
        phone = request.form.get("phone", "").strip()
        farming_type = request.form.get("farming_type", "").strip()
        address = request.form.get("address", "").strip()

        if not name or not phone:
            return render_template("farmer_register.html")

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO farmer (name, aadhaar, phone, farming_type, address)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (name, aadhaar, phone, farming_type, address),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

        return redirect("/farmer_details")
    return render_template("farmer_register.html")


# Farmer Details Route (Display all or searched farmers)
@app.route("/farmer_details")
def farmer_details():
    query = request.args.get("q", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if query:
            like = f"%{query}%"
            cursor.execute(
                """
                SELECT * FROM farmer
                WHERE name LIKE %s OR phone LIKE %s OR farming_type LIKE %s OR address LIKE %s
                """,
                (like, like, like, like),
            )
        else:
            cursor.execute("SELECT * FROM farmer")
        farmers = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template("farmer_details.html", farmers=farmers, query=query)


# Update Farmer Route
@app.route("/update_farmer", methods=["POST"])
def update_farmer():
    farmer_id = request.form.get("id", "").strip()
    name = request.form.get("name", "").strip()
    aadhaar = request.form.get("aadhaar", "").strip()
    phone = request.form.get("phone", "").strip()
    farming_type = request.form.get("farming_type", "").strip()
    address = request.form.get("address", "").strip()

    if not farmer_id:
        return "", 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE farmer
            SET name = %s, aadhaar = %s, phone = %s, farming_type = %s, address = %s
            WHERE id = %s
            """,
            (name, aadhaar, phone, farming_type, address, farmer_id),
        )
        conn.commit()
    except Error:
        conn.rollback()
        return "", 500
    finally:
        cursor.close()
        conn.close()

    return "", 204


# Delete Farmer Route
@app.route("/delete_farmer", methods=["POST"])
def delete_farmer():
    farmer_id = request.form.get("id", "").strip()
    if not farmer_id:
        return "", 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM farmer WHERE id = %s", (farmer_id,))
        conn.commit()
    except Error:
        conn.rollback()
        return "", 500
    finally:
        cursor.close()
        conn.close()

    return "", 204


# Sell Agro Products Route
@app.route("/sell_agro_products", methods=["GET", "POST"])
def sell_agro_products():
    if request.method == "POST":
        product_name = request.form.get("product_name", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", "").strip()
        email = request.form.get("email", "").strip()

        if not product_name or not price:
            return render_template("sell_agro_products.html")

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO produc (product_name, description, price, email)
                VALUES (%s, %s, %s, %s)
                """,
                (product_name, description, price, email),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

        return redirect("/agro_products")
    return render_template("sell_agro_products.html")


# Display Agro Products Route
@app.route("/agro_products")
def agro_products():
    query = request.args.get("q", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if query:
            like = f"%{query}%"
            cursor.execute(
                "SELECT * FROM produc WHERE product_name LIKE %s OR description LIKE %s",
                (like, like),
            )
        else:
            cursor.execute("SELECT * FROM produc")
        products = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template("agro_products.html", products=products, query=query)


# Route to display farmer registration and deletion records
@app.route("/farmer_records")
def farmer_records():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT name, aadhaar, phone, action, timestamp
            FROM farmer_records
            ORDER BY timestamp DESC
            """
        )
        records = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template("records.html", records=records)


# Quick summary endpoint for demo/inspection
@app.route("/api/summary")
def api_summary():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM farmer")
        farmer_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM produc")
        product_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM farmer_records")
        record_count = cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()

    return {
        "project": "Farm Management System",
        "year": 2026,
        "author": "Shani",
        "farmers": farmer_count,
        "products": product_count,
        "audit_records": record_count,
    }


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
