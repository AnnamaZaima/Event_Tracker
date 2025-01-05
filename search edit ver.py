@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            try:
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)
                # Search in event name and details
                search_query = """
                SELECT * FROM post 
                WHERE Event_name LIKE %s OR details LIKE %s
                """
                cursor.execute(search_query, (f"%{query}%", f"%{query}%"))
                results = cursor.fetchall()
                cursor.close()
                connection.close()
                return render_template('search_results.html', query=query, results=results)
            except mysql.connector.Error as err:
                flash(f"Database error: {err}", "danger")
                return redirect('/')
        else:
            flash("Please enter a search term.", "danger")
            return redirect('/')
    return redirect('/')
