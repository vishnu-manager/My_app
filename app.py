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
# Route for home page (login)
@app.route("/")
def home():
    return render_template("home.html")

# Login route
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    cur.execute("SELECT role FROM users WHERE email=%s AND password=%s", (email, password))
    result = cur.fetchone()

    if result:
        role = result[0]
        session["user"] = email
        session["role"] = role
        if role == "admin":
            return jsonify({"redirect_url": "/admin_dashboard"})
        else:
            return jsonify({"redirect_url": "/resident_dashboard"})
    else:
        return jsonify({"message": "Invalid email or password."})

# Admin registration page
@app.route("/admin_register")
def admin_register():
    return render_template("admin_register.html")

# Resident registration page
@app.route("/resident_register")
def resident_register():
    return render_template("resident_register.html")

# Admin Dashboard
@app.route("/admin_dashboard")
def admin_dashboard():
    if "user" not in session or session["role"] != "admin":
        return redirect("/")
    return render_template("admin_dashboard.html")

# Resident Dashboard
@app.route("/resident_dashboard")
def resident_dashboard():
    if "user" not in session or session["role"] != "resident":
        return redirect("/")
    return render_template("resident_dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)

