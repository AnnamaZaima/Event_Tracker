from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'eventify'
}

# Establish database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/', methods=['GET', 'POST'])
def event_post():
    if request.method == 'POST':
        event_name = request.form.get('event_name')
        username = request.form.get('username')
        event_details = request.form.get('event_details')
        event_date = request.form.get('event_date')
        event_link = request.form.get('event_link')

        if event_name and username and event_details and event_date:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO event (Event_name, username, details, Event_date, Event_link) VALUES (%s, %s, %s, %s, %s)",
                (event_name, username, event_details, event_date, event_link)
            )
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('event_post'))

    # Fetch all posts for display
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM event")
    posts = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('event_post.html', posts=posts)

@app.route('/delete/<int:event_id>', methods=['POST'])
def delete_post(event_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Delete from child tables
    cursor.execute("DELETE FROM competition WHERE Event_id = %s", (event_id,))
    cursor.execute("DELETE FROM fest WHERE Event_id = %s", (event_id,))
    cursor.execute("DELETE FROM seminar WHERE Event_id = %s", (event_id,))
    # Delete from main event table
    cursor.execute("DELETE FROM event WHERE Event_id = %s", (event_id,))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('event_post'))

@app.route('/options', methods=['GET', 'POST'])
def event_options():
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        selected_options = request.form.getlist('event_type')

        connection = get_db_connection()
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
        return redirect(url_for('event_post'))

    return render_template('event_options.html')

if __name__ == '__main__':
    app.run(debug=True)
