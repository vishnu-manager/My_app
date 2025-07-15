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

# Run the app locally
if __name__ == '__main__':
    app.run(debug=True)
