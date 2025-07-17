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


return conn
# Route for home page (login)
@app.route("/")
def home():
    return render_template("home.html")

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT role FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            session['email'] = email
            session['role'] = user[0]
            if user[0] == 'admin':
                return redirect('/admin_dashboard')
            else:
                return redirect('/resident_dashboard')
        else:
            return "Invalid credentials"

    return render_template('login.html')

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

