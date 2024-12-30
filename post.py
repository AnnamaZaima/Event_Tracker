from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

posts = []

@app.route('/', methods=['GET', 'POST'])
def event_post():
    if request.method == 'POST':
        event_name = request.form.get('event_name')
        event_details = request.form.get('event_details')
        event_date = request.form.get('event_date')
        event_location = request.form.get('event_location')

        if event_name and event_details and event_date and event_location:
            event_date = datetime.strptime(event_date, '%Y-%m-%d')
            post = {
                'id': len(posts) + 1,
                'name': event_name,
                'details': event_details,
                'date': event_date,
                'location': event_location
            }
            posts.append(post)
            return redirect(url_for('event_post'))

    return render_template('event_post.html', posts=posts)

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    global posts
    posts = [post for post in posts if post['id'] != post_id]
    return redirect(url_for('event_post'))

if __name__ == '__main__':
    app.run(debug=True)
