from flask import Flask, render_template, request, jsonify, redirect, url_for
import pymysql
import pymysql.cursors

app = Flask(__name__)

# MySQL config (update with your credentials)
db = pymysql.connect(
    host='localhost',
    user='root',
    password='Reddy123@',
    database='myapp',
    cursorclass=pymysql.cursors.DictCursor
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
        with db.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s AND password = %s"
            cursor.execute(sql, (email, password))
            user = cursor.fetchone()

            if user:
                # Redirect based on role (if your table has a 'role' column)
                if user.get('role') == 'admin':
                    return jsonify({"redirect_url": "/admin_dashboard"})
                else:
                    return jsonify({"redirect_url": "/resident_dashboard"})
            else:
                return jsonify({"message": "Invalid email or password"})
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Internal server error"})

# Run app
if __name__ == '__main__':
    app.run(debug=True)
