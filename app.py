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
# Home / Admin Dashboard
@app.route("/admin_dashboard")
def admin_dashboard():
    if "role" in session and session["role"] == "admin":
        cursor.execute("SELECT name, contact FROM maintainers")
        maintainers = cursor.fetchall()
        return render_template("admin_dashboard.html", maintainers=[{'name': m[0], 'contact': m[1]} for m in maintainers])
    return redirect("/login")

# Add Maintainer
@app.route("/add_maintainer", methods=["POST"])
def add_maintainer():
    data = request.get_json()
    name = data.get("name")
    contact = data.get("contact")
    job_title = data.get("job_title")
    
    try:
        cursor.execute("INSERT INTO maintainers (name, contact, job_title) VALUES (%s, %s, %s)", (name, contact, job_title))
        conn.commit()
        return jsonify({"message": "Maintainer added successfully!"})
    except Exception as e:
        return jsonify({"message": str(e)})

# Upload Image
@app.route("/upload_image", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return "No image part", 400
    
    file = request.files["image"]
    if file.filename == "":
        return "No selected file", 400
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return redirect("/admin_dashboard")

# Remove Resident
@app.route("/remove_resident", methods=["POST"])
def remove_resident():
    data = request.get_json()
    email = data.get("email")
    try:
        cursor.execute("DELETE FROM residents WHERE email = %s", (email,))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

# Add Complaint
@app.route("/add_complaint", methods=["POST"])
def add_complaint():
    data = request.get_json()
    complaint = data.get("complaint")
    try:
        cursor.execute("INSERT INTO complaints (text) VALUES (%s)", (complaint,))
        conn.commit()
        return jsonify({"message": "Complaint submitted successfully!"})
    except Exception as e:
        return jsonify({"message": str(e)})

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# Login Dummy Page
@app.route("/login")
def login():
    return "Login Page Placeholder"

if __name__ == '__main__':
    app.run(debug=True)

