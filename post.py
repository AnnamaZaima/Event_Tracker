@app.route('/event_post', methods=['GET', 'POST'])
def event_post():
    if request.method == 'POST':
        # Collect event details
        event_name = request.form.get('event_name')
        username = request.form.get('username')
        event_details = request.form.get('event_details')
        event_date = request.form.get('event_date')
        event_link = request.form.get('event_link')
        selected_options = request.form.getlist('event_type')  # Collect selected options

        # Insert event details into the database
        if event_name and username and event_details and event_date:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO event (Event_name, username, details, Event_date, Event_link) VALUES (%s, %s, %s, %s, %s)",
                (event_name, username, event_details, event_date, event_link)
            )
            event_id = cursor.lastrowid  # Get the ID of the newly created event

            # Insert options into their respective tables
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

    # Fetch all posts along with their options for display
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM event")
    posts = cursor.fetchall()

    # Fetch options for each event
    for post in posts:
        event_id = post['Event_id']
        cursor.execute("SELECT * FROM competition WHERE Event_id = %s", (event_id,))
        post['competitions'] = cursor.fetchall()
        cursor.execute("SELECT * FROM fest WHERE Event_id = %s", (event_id,))
        post['fests'] = cursor.fetchall()
        cursor.execute("SELECT * FROM seminar WHERE Event_id = %s", (event_id,))
        post['seminars'] = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('/post.html', posts=posts)


@app.route('/delete_post/<int:event_id>', methods=['POST'])
def delete_post(event_id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Delete the event and its related options
    cursor.execute("DELETE FROM competition WHERE Event_id = %s", (event_id,))
    cursor.execute("DELETE FROM fest WHERE Event_id = %s", (event_id,))
    cursor.execute("DELETE FROM seminar WHERE Event_id = %s", (event_id,))
    cursor.execute("DELETE FROM event WHERE Event_id = %s", (event_id,))
    connection.commit()

    cursor.close()
    connection.close()
    return redirect('/event_post')
