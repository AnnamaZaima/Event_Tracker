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
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)

            # Check if the email already exists in the user table
                query = "SELECT * FROM user WHERE gsuite = %s"
                cursor.execute(query, (email,))
                result = cursor.fetchone()
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
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM event")
                posts = cursor.fetchall()
                cursor.close()
                connection.close()
                return render_template('user_dashboard.html', email=email[0].upper(), id=id, posts=posts)
            else:
                flash('User not found.', 'danger')
                return redirect('/login')
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
            return redirect('/login')
    else:
        flash('Please log in first.', 'danger')
        return redirect('/login')
   
    
   


@app.route('/ticket', methods=['GET'])
def ticket():
  if 'email' in session:
   user_email = session['email']
   ticket_status = request.args.get('status', 'all')
   try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    if ticket_status == 'all':
        query = """
            SELECT ticket_id, subject, status, created_at, response, club_name
            FROM ticket WHERE user_email = %s
        """
        cursor.execute(query, (user_email,))
    else:
        query = """
            SELECT ticket_id, subject, status, created_at, response, club_name
            FROM ticket WHERE user_email = %s AND status = %s
        """
        cursor.execute(query, (user_email, ticket_status))

    tickets = cursor.fetchall()
    name=user_email.split(".")
    return render_template('/ticket.html', tickets=tickets, username=name[0].upper(), filter=ticket_status)
   except mysql.connector.Error as err:
      flash(f"Error: {err}", 'danger')
      return redirect('/ticket')
  return render_template('/ticket.html')





@app.route('/admin_ticket', methods=['GET'])
def admin_ticket():
  if 'username' in session:
   username = session['username']
   try:
      conn = mysql.connector.connect(**db_config)
      cursor = conn.cursor(dictionary=True)
      cursor.execute("SELECT club_name FROM club WHERE username = %s", (username,))
      club = cursor.fetchone()
      if club:
         club_name = club['club_name']
         ticket_status = request.args.get('status', 'all')
         if ticket_status == 'all':
            query = """
            SELECT ticket_id, user_email, subject, message, status, created_at, response
            FROM ticket WHERE club_name = %s
             """
            cursor.execute(query, (club_name,))
         else:
            query = """
            SELECT ticket_id, user_email, subject, message, status, created_at, response
            FROM ticket WHERE club_name = %s AND status = %s
            """
            cursor.execute(query, (club_name, ticket_status))
         tickets = cursor.fetchall()
         return render_template('admin_ticket.html', tickets=tickets, club_name=club_name, filter=ticket_status)
   except mysql.connector.Error as err:
      flash(f"Error: {err}", 'danger')
      return redirect('/admin_ticket')
   return render_template('/admin_ticket.html')
 


@app.route('/submit_ticket', methods=['POST'])
def submit_ticket():
      # Replace with logged-in user's email
    club_name = request.form['club_name']
    subject = request.form['subject']
    message = request.form['message']
    if 'email' in session:
      user_email = session['email']
      try:
         conn = mysql.connector.connect(**db_config)
         cursor = conn.cursor(dictionary=True)

    # Insert the ticket into the database
    
         query = """ INSERT INTO ticket (user_email, club_name, subject, message, status) VALUES (%s, %s, %s, %s, 'open')"""
         cursor.execute(query, (user_email, club_name, subject, message))
         conn.commit()

         cursor.close()
         conn.close()
         return redirect('/ticket')
      except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
            return redirect('/ticket')
    return redirect('/ticket')


@app.route('/club/respond/<int:ticket_id>', methods=['POST'])
def respond_ticket(ticket_id):
    response = request.form['response']
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
                try:
                  conn = mysql.connector.connect(**db_config)
                  cursor = conn.cursor(dictionary=True)
                  query = """
                     UPDATE ticket
                     SET response = %s, status = 'closed'
                     WHERE ticket_id = %s AND club_name = %s AND status = 'open'
                     """
                  cursor.execute(query, (response, ticket_id, club_name))
                  conn.commit()
                  cursor.close()
                  conn.close()
                  return redirect('/admin_ticket')
                except mysql.connector.Error as err:
                   flash(f"Error: {err}", 'danger')
                   return redirect('/ticket')
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
            return redirect('/ticket')
    return redirect('/ticket')

#posting_event
@app.route('/event_post', methods=['GET', 'POST'])
def event_post():
    if request.method == 'POST':
        event_name = request.form.get('event_name')
        username = request.form.get('username')
        event_details = request.form.get('event_details')
        event_date = request.form.get('event_date')
        event_link = request.form.get('event_link')

        if event_name and username and event_details and event_date:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO event (Event_name, username, details, Event_date, Event_link) VALUES (%s, %s, %s, %s, %s)",
                (event_name, username, event_details, event_date, event_link)
            )
            connection.commit()
            cursor.close()
            connection.close()
            return redirect('/event_post')

    # Fetch all posts for display
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM event")
    posts = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('/post.html', posts=posts)

@app.route('/delete/<int:event_id>', methods=['POST'])
def delete_post(event_id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM event WHERE Event_id = %s", (event_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect('/event_post')

@app.route('/options', methods=['GET', 'POST'])
def event_options():
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        selected_options = request.form.getlist('event_type')

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        for option in selected_options:
            time = request.form.get(f'time_{option}')
            title = request.form.get(f'title_{option}')
            details = request.form.get(f'details_{option}')
            location = request.form.get(f'location_{option}')
            extra_field = request.form.get(f'extra_field_{option}', None)

            if option == 'competition':
                cursor.execute(
                    "INSERT INTO competition (Event_id, time, title, details, location, enroll) VALUES (%s, %s, %s, %s, %s, %s)",
                    (event_id, time, title, details, location, extra_field)
                )
            elif option == 'fest':
                cursor.execute(
                    "INSERT INTO fest (Event_id, time, title, details, location) VALUES (%s, %s, %s, %s, %s)",
                    (event_id, time, title, details, location)
                )
            elif option == 'seminar':
                cursor.execute(
                    "INSERT INTO seminar (Event_id, registration, time, title, details, location) VALUES (%s, %s, %s, %s, %s, %s)",
                    (event_id, extra_field, time, title, details, location)
                )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect('/event_post')
    return render_template('/post.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
