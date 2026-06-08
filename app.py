import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# DATABASE SETUP

conn = sqlite3.connect('database.db')

conn.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
)
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    category TEXT,
    priority TEXT,
    status TEXT
)
''')

conn.close()


# AI CATEGORY

def analyze_complaint(text):

    text = text.lower()

    if "water" in text:
        return "Water Issue"
    elif "electricity" in text:
        return "Electricity Issue"
    elif "road" in text:
        return "Road Issue"
    elif "garbage" in text:
        return "Garbage Issue"
    elif "hospital" in text:
        return "Health Issue"
    elif "internet" in text:
        return "Network Issue"
    else:
        return "General Complaint"


# AI PRIORITY

def detect_priority(text):

    text = text.lower()

    if "emergency" in text:
        return "High"
    elif "urgent" in text:
        return "Medium"
    else:
        return "Low"


# HOME

@app.route('/')
def home():
    return render_template('index.html')


# REGISTER

@app.route('/register', methods=['GET', 'POST'])
def register():

    message = ""

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        try:
            conn = sqlite3.connect('database.db')

            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )

            conn.commit()
            conn.close()

            message = "Registration Successful!"

        except:
            message = "Email Already Exists"

    return render_template(
        'register.html',
        message=message
    )


# LOGIN

@app.route('/login', methods=['GET', 'POST'])
def login():

    message = ""

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')

        cursor = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            return redirect('/dashboard')
        else:
            message = "Invalid Email Or Password"

    return render_template(
        'login.html',
        message=message
    )


# DASHBOARD

@app.route('/dashboard')
def dashboard():

    conn = sqlite3.connect('database.db')

    total = conn.execute(
        "SELECT COUNT(*) FROM complaints"
    ).fetchone()[0]

    high = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE priority='High'"
    ).fetchone()[0]

    pending = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE status='Pending'"
    ).fetchone()[0]

    conn.close()

    return render_template(
        'dashboard.html',
        total=total,
        high=high,
        pending=pending
    )


# COMPLAINT

@app.route('/complaint', methods=['GET', 'POST'])
def complaint():

    message = ""

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']

        category = analyze_complaint(description)
        priority = detect_priority(description)

        conn = sqlite3.connect('database.db')

        conn.execute(
            "INSERT INTO complaints(title, description, category, priority, status) VALUES (?, ?, ?, ?, ?)",
            (title, description, category, priority, "Pending")
        )

        conn.commit()
        conn.close()

        message = "Complaint Submitted Successfully!"

    conn = sqlite3.connect('database.db')

    cursor = conn.execute(
        "SELECT title, description, category, priority, status FROM complaints"
    )

    complaints = []

    for row in cursor:
        complaints.append({
            'title': row[0],
            'description': row[1],
            'category': row[2],
            'priority': row[3],
            'status': row[4]
        })

    conn.close()

    return render_template(
        'complaint.html',
        complaints=complaints,
        message=message
    )


# ADMIN

@app.route('/admin')
def admin():

    conn = sqlite3.connect('database.db')

    cursor = conn.execute(
        "SELECT title, description, category, priority, status FROM complaints"
    )

    complaints = []

    for row in cursor:
        complaints.append({
            'title': row[0],
            'description': row[1],
            'category': row[2],
            'priority': row[3],
            'status': row[4]
        })

    conn.close()

    return render_template(
        'admin.html',
        complaints=complaints
    )


# LOGOUT

@app.route('/logout')
def logout():
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)