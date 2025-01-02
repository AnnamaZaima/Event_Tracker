from flask import Flask, render_template,session, request, redirect, url_for, flash
import mysql.connector
import re

app = Flask(__name__)
app.secret_key = "shafin"  # Change this to a strong secret key

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'eventify'
}

# Route for home page
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        user_id = request.form['id']

        # Check if email ends with valid domain
        if not (email.endswith('@bracu.ac.bd') or email.endswith('@g.bracu.ac.bd')):
            flash("Invalid email domain", "danger")
            return redirect('/login')

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)

            # Check if the email already exists in the user table
            query = "SELECT * FROM user WHERE gsuite = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            print(result)
            if result:
                # Email exists, check if the IDs match
                if result['id'] == user_id:
                    session['email'] = result['gsuite']
                    return redirect('/user_dashboard')
                else:
                    flash("ID does not match for the provided email.", "danger")
                    return redirect('/login')
            else:
                # Email does not exist, insert new record
                insert_query = "INSERT INTO user (gsuite, id) VALUES (%s, %s)"
                cursor.execute(insert_query, (email, user_id))
                connection.commit()
                session['email'] = result['gsuite']
                return redirect('/user_dashboard')

        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")
            return redirect(url_for('/login'))

        finally:
            cursor.close()
            connection.close()

    return render_template('login.html')


# Route for signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        club_name = request.form['club_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO club (club_name, username, club_email, password)
                VALUES (%s, %s, %s, %s)
            """, (club_name, username, email, password))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/club_login')
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
            return redirect('/signup')
    return render_template('signup.html')

# Route for club_login
@app.route('/club_login', methods=['GET', 'POST'])
def club_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM club WHERE username = %s AND password = %s
            """, (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                session['username'] = user['username']
                return redirect('/dashboard')
            else:
                flash('Invalid username or password.', 'danger')
                return redirect('/club_login')
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
            return redirect('/club_login')
    return render_template('club_login.html')

# Route for dashboard (protected page)
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT club_name FROM club WHERE username = %s", (username,))
            club = cursor.fetchone()
            cursor.close()
            conn.close()

            if club:
                club_name = club['club_name']
                return render_template('dashboard.html', username=username, club_name=club_name)
            else:
                flash('User not found.', 'danger')
                return redirect('/login')
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
            return redirect('/login')
    else:
        flash('Please log in first.', 'danger')
        return redirect('/login')
# userDashboard route
@app.route('/user_dashboard')
def user_dashboard():
    if 'email' in session:
        email = session['email']
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM user WHERE gsuite = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                email=email.split(".")
                id = user['id']
                return render_template('user_dashboard.html', email=email[0].upper(), id=id)
            else:
                flash('User not found.', 'danger')
                return redirect('/login')
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
            return redirect('/login')
    else:
        flash('Please log in first.', 'danger')
        return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
