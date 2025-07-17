from flask import Flask, render_template, request, redirect, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "apartment_secret"


# Database connection
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "dpg-d1rnu3p5pdvs73ebrbig-a"),
    port=os.getenv("DB_PORT", "5432"),
    database=os.getenv("DB_NAME", "myapp123"),
    user=os.getenv("DB_USER", "vishnu123"),
    password=os.getenv("DB_PASSWORD", "Vj2NZiDD7hd61b7KFz3iC5xZtCpZaaVY")
)


cursor = conn.cursor()
@app.route("/")
def home():
    return redirect("/login_page")  # or render_template("home.html")

@app.route("/login")
def login_redirect():
    return redirect("/login_page")
# Login Page Route
@app.route("/login_page")
def login_page():
    return render_template("home.html")


# Admin Dashboard Route
@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if "user" not in session or session["role"] != "admin":
        return redirect("/login_page")

    apartment_code = session.get("apartment_code")

    # Fetch apartment details
    cursor.execute("SELECT * FROM apartments WHERE code = %s", (apartment_code,))
    apartment = cursor.fetchone()

    # Fetch residents
    cursor.execute("SELECT * FROM users WHERE role = 'resident' AND apartment_code = %s", (apartment_code,))
    residents = cursor.fetchall()

    # Fetch maintainers
    cursor.execute("SELECT * FROM maintainers WHERE apartment_code = %s", (apartment_code,))
    maintainers = cursor.fetchall()

    # Fetch maintenance records
    cursor.execute("SELECT * FROM maintenance WHERE apartment_code = %s", (apartment_code,))
    maintenance_records = cursor.fetchall()

    # Handle Form Submissions
    if request.method == "POST":
        form_type = request.form.get("form_type")

        if form_type == "add_maintainer":
            maintainer_name = request.form["maintainer_name"]
            maintainer_contact = request.form["maintainer_contact"]

            try:
                cursor.execute(
                    "INSERT INTO maintainers (name, contact, apartment_code) VALUES (%s, %s, %s)",
                    (maintainer_name, maintainer_contact, apartment_code)
                )
                conn.commit()
            except Exception as e:
                print("Error adding maintainer:", e)

        elif form_type == "add_maintenance":
            resident_name = request.form["resident_name"]
            flat_number = request.form["flat_number"]
            amount = request.form["amount"]

            try:
                cursor.execute(
                    "INSERT INTO maintenance (resident_name, flat_number, amount_paid, apartment_code) VALUES (%s, %s, %s, %s)",
                    (resident_name, flat_number, amount, apartment_code)
                )
                conn.commit()
            except Exception as e:
                print("Error adding maintenance record:", e)

        return redirect("/admin_dashboard")

    return render_template(
        "admin_dashboard.html",
        apartment=apartment,
        residents=residents,
        maintainers=maintainers,
        maintenance_records=maintenance_records
    )


if __name__ == '__main__':
    app.run(debug=True)

