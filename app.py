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

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()
        if result:
            session['username'] = username
            session['role'] = result[0]
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'role' in session:
        if session['role'] == 'admin':
            return render_template('admin_dashboard.html')
        else:
            return render_template('resident_dashboard.html')
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

