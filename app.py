from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import psycopg2
from psycopg2.extras import RealDictCursor, DictCursor
import os


app = Flask(__name__)


# Database connection
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "dpg-d1rnu3p5pdvs73ebrbig-a"),
    port=os.getenv("DB_PORT", "5432"),
    database=os.getenv("DB_NAME", "myapp123"),
    user=os.getenv("DB_USER", "vishnu123"),
    password=os.getenv("DB_PASSWORD", "Vj2NZiDD7hd61b7KFz3iC5xZtCpZaaVY")
)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html')  # Return login form

    # POST: Handle login form submission
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()
            if user:
                session['user'] = dict(user)
                if user['role'] == 'admin':
                    return jsonify({'redirect': url_for('admin_dashboard')})
                else:
                    return jsonify({'redirect': url_for('resident_dashboard')})
            else:
                return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        print("Login Error:", e)
        return jsonify({'message': 'Internal server error'}), 500

# ✅ Admin Register Page - GET & POST
@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'GET':
        return render_template('admin_register.html')  # HTML file in /templates

    # POST: Save admin
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    apartment_code = data.get("apartment_code")

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"message": "Email already registered!"}), 409

            cursor.execute(
                "INSERT INTO users (name, email, password, role, apartment_code) VALUES (%s, %s, %s, %s, %s)",
                (name, email, password, role, apartment_code)
            )
            conn.commit()
            return jsonify({
                "message": "Admin registered successfully!",
                "redirect_url": "/"
            }), 201
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Registration failed!"}), 500



# Admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, contact FROM maintainers")
            maintainers = cursor.fetchall()
            maintainers = [{'name': m[0], 'contact': m[1]} for m in maintainers]
        return render_template('admin_dashboard.html', maintainers=maintainers)
    except Exception as e:
        print("Error:", e)
        return "Error loading dashboard"

# Add maintainer
@app.route('/add_maintainer', methods=['POST'])
def add_maintainer():
    data = request.get_json()
    name = data.get("name")
    contact = data.get("contact")
    job_title = data.get("job_title")

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO maintainers (name, contact, job_title) VALUES (%s, %s, %s)",
                (name, contact, job_title)
            )
            conn.commit()
        return jsonify({"message": "Maintainer added successfully!"})
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Error adding maintainer!"}), 500
@app.route('/get_residents', methods=['GET'])
def get_residents():
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT name, flat_number, apartment_code FROM users WHERE role = 'resident'")
            residents = cursor.fetchall()
            return jsonify(residents)
    except Exception as e:
        print("Error fetching residents:", e)
        return jsonify([]), 500
@app.route('/admin_residents', methods=['GET'])
def admin_residents():
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT name, flat_number, email, apartment_code FROM users WHERE role = 'resident'")
            rows = cursor.fetchall()
            residents = [dict(row) for row in rows]
            return render_template('admin_residents.html', residents=residents)
    except Exception as e:
        print("Error fetching residents:", e)
        return "Internal Server Error", 500
@app.route('/remove_resident', methods=['POST'])
def remove_resident():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"success": False, "message": "Email is required."}), 400

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE email = %s AND role = 'resident'", (email,))
            if cursor.rowcount == 0:
                return jsonify({"success": False, "message": "Resident not found."}), 404

            conn.commit()
            return jsonify({"success": True})
    except Exception as e:
        conn.rollback()
        print("Error deleting resident:", e)
        return jsonify({"success": False, "message": "Internal server error."}), 500

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')  # Or replace 'home' with your login or landing page route









# ✅ Resident Register Page - GET & POST
@app.route('/resident_register', methods=['GET', 'POST'])
def resident_register():
    if request.method == 'GET':
        return render_template('resident_register.html')

    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    flat_number = data.get("flat_number")
    role = data.get("role")
    apartment_code = data.get("apartment_code")

    try:
        with conn.cursor() as cursor:
            # Check if apartment code exists
            cursor.execute("SELECT * FROM apartments WHERE apartment_code = %s", (apartment_code,))
            if cursor.fetchone() is None:
                return jsonify({"message": "Invalid apartment code!"}), 400

            # Check if email already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"message": "Email already exists!"}), 409

            # Insert user
            cursor.execute(
                "INSERT INTO users (name, email, password, role, flat_number, apartment_code) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, email, password, role, flat_number, apartment_code)
            )
            conn.commit()
            return jsonify({"message": "Resident registered successfully!"}), 201

    except Exception as e:
        conn.rollback()  # ✅ properly indented
        print("Error:", e)
        return jsonify({"message": "Internal server error!"}), 500

@app.route('/resident_dashboard')
def resident_dashboard():
    # Check login session
    if 'user_id' not in session or session.get('role') != 'resident':
        return redirect(url_for('login'))

    user_id = session['user_id']

    try:
        with conn.cursor() as cursor:
            # ✅ Fetch resident info
            cursor.execute("""
                SELECT name, email, flat_number, apartment_code 
                FROM users 
                WHERE id = %s
            """, (user_id,))
            user_row = cursor.fetchone()

            if not user_row:
                return redirect(url_for('login'))

            resident = {
                "name": user_row[0],
                "email": user_row[1],
                "flat_number": user_row[2],
                "apartment_code": user_row[3]
            }

            # ✅ Fetch maintainers for this apartment code
            cursor.execute("""
                SELECT name, contact, job_title 
                FROM maintainers 
                WHERE apartment_code = %s
            """, (resident["apartment_code"],))
            maintainer_rows = cursor.fetchall()

            maintainers = []
            for row in maintainer_rows:
                maintainers.append({
                    "name": row[0],
                    "contact": row[1],
                    "job_title": row[2]
                })

            # ✅ Render dashboard
            return render_template("resident_dashboard.html", resident=resident, maintainers=maintainers)

    except Exception as e:
       conn.rollback()  # <- ADD THIS
       print("Error:", e)
       return jsonify({"message": "Internal server error!"}), 500

# Root
@app.route('/')
def home():
    return render_template('index.html')

# Run the app locally
if __name__ == '__main__':
    app.run(debug=True)

