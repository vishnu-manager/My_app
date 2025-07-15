from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import psycopg2
import psycopg2.extras

app = Flask(__name__)

# Database connection
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "dpg-d1r8cremcj7s73akrs9g-a"),
    port=os.getenv("DB_PORT", "5432"),
    database=os.getenv("DB_NAME", "myapp_llm7"),
    user=os.getenv("DB_USER", "myapp_llm7_user"),
    password=os.getenv("DB_PASSWORD", "aGOHL6YzcMT0okNlwevJrmpjfzYCDkYa")
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()

            if user:
                role = user.get('role')  # Make sure 'role' exists in your DB table
                if role == 'admin':
                    return jsonify({"redirect_url": "/admin_dashboard"})
                else:
                    return jsonify({"redirect_url": "/resident_dashboard"})
            else:
                return jsonify({"message": "Invalid email or password"})
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Internal server error"})
@app.route('/admin_register', methods=['POST'])
def admin_register():
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
            return jsonify({"message": "Admin registered successfully!"}), 201
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Registration failed!"}), 500

@app.route('/resident_register', methods=['POST'])
def resident_register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    flat_number = data.get("flat_number")
    role = data.get("role")
    apartment_code = data.get("apartment_code")

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"message": "Email already exists!"}), 409

            cursor.execute(
                "INSERT INTO users (name, email, password, role, flat_number, apartment_code) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, email, password, role, flat_number, apartment_code)
            )
            conn.commit()
            return jsonify({"message": "Resident registered successfully!"}), 201
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Internal server error!"}), 500

# Run the app locally
if __name__ == '__main__':
    app.run(debug=True)
