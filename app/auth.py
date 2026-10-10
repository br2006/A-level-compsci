from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import UserMixin, login_user, logout_user, login_required, login_manager, current_user
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

class User(UserMixin):
    def __init__(self, id, firstname, lastname, username, email, age, profile_pic, date_joined, password):
        self.id = id
        self.email = email
        self.password = password

        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.age = age
        self.profile_pic = profile_pic
        self.date_joined = date_joined

def get_user_by_id(user_id):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7], user[8])
    return None

def get_user_by_email(email):
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7], user[8])
    return None

@auth.route('/login')
def login():
    return render_template('user/log.html', current_url = request.url)

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    user = get_user_by_email(email)
    
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))
    
    login_user(user)
    return redirect(url_for('main.index'))

@auth.route('/signup')
def signup():
    return render_template('user/signup.html', current_url = request.url)

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    password = request.form.get('password')

    name1 = request.form.get('firstname')
    name2 = request.form.get('lastname')
    uname = request.form.get('username')
    age = request.form.get('age')
    pic = 1

    
    user = get_user_by_email(email)
    
    if user:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))
    
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    # cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, generate_password_hash(password, method='sha256')))
    cursor.execute("INSERT INTO Users(firstname, lastname, username, email, age, profile_pic, date_joined, password) VALUES(?, ?, ?, ?, ?, ?, datetime('now'), ?)", [name1, name2, uname, email, age, pic, generate_password_hash(password)])
    conn.commit()
    conn.close()

    user = get_user_by_email(email)
    login_user(user)
    return redirect(url_for('main.index'))
    
    # return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


def unauthorised():
    return "you're not signed in!"