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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        cursor.execute("SELECT role, username FROM users WHERE email=%s AND password=%s", (email, password))
        result = cursor.fetchone()

        if result:
            session['username'] = result[1]
            session['role'] = result[0]
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template("login.html")


@app.route('/dashboard')
def dashboard():
    if 'role' in session:
        if session['role'] == 'admin':
            return redirect("/admin_dashboard")
        else:
            return render_template('resident_dashboard.html')
    return redirect('/login')


@app.route("/admin_dashboard")
def admin_dashboard():
    if "role" in session and session["role"] == "admin":
        cursor.execute("SELECT name, contact FROM maintainers")
        maintainers = cursor.fetchall()
        return render_template("admin_dashboard.html", maintainers=[{'name': m[0], 'contact': m[1]} for m in maintainers])
    return redirect("/login")


@app.route("/add_maintainer", methods=["POST"])
def add_maintainer():
    name = request.form.get("name")
    contact = request.form.get("contact")
    job_title = request.form.get("job_title")

    try:
        cursor.execute("INSERT INTO maintainers (name, contact, job_title) VALUES (%s, %s, %s)",
                       (name, contact, job_title))
        conn.commit()
        return redirect("/admin_dashboard")
    except Exception as e:
        return jsonify({"message": str(e)})


@app.route("/upload_image", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return "No image part", 400

    file = request.files["image"]
    if file.filename == "":
        return "No selected file", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    return redirect("/admin_dashboard")


@app.route("/remove_resident", methods=["POST"])
def remove_resident():
    email = request.form.get("email")
    try:
        cursor.execute("DELETE FROM residents WHERE email = %s", (email,))
        conn.commit()
        return redirect("/admin_dashboard")
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/add_complaint", methods=["POST"])
def add_complaint():
    complaint = request.form.get("complaint")
    try:
        cursor.execute("INSERT INTO complaints (text) VALUES (%s)", (complaint,))
        conn.commit()
        return jsonify({"message": "Complaint submitted successfully!"})
    except Exception as e:
        return jsonify({"message": str(e)})


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")



if __name__ == '__main__':
    app.run(debug=True)

