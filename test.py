from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
import bcrypt
from flask_mysqldb import MySQL

app = Flask(__name__)

#MYSQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'eventify'
app.secret_key = 'your_secret_key_here'

mysql = MySQL(app)

class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

@app.route('/test_db')
def test_db():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SHOW DATABASES;")
        databases = cursor.fetchall()
        cursor.close()
        return f"Databases: {databases}"
    except Exception as e:
        return f"Error: {e}"

@app.route('/Login')
def login():
    return render_template('login.html')

@app.route('/signup', methods = ['GET','POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            club_name = form.name.data
            username = request.form.get('username')
            club_email = form.email.data
            password = form.password.data

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            #store data in database
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO club (club_name, username, club_email, password) VALUES (%s, %s, %s, %s)", (club_name, username, club_email, hashed_password))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('club_login'))
        except Exception as e:
            print(f"Database error: {e}")
            return "An error occurred during registration."

    
    return render_template('signup.html', form=form)

@app.route('/club_login')
def club_login():
    return render_template('club_login.html')

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

if __name__ == '__main__':
    app.run(debug=True)
