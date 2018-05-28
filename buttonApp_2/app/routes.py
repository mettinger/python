from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from app.models import User

from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from flask import send_file

from flask import request
from werkzeug.urls import url_parse

from app import db
from app.forms import RegistrationForm

import sqlite3
import tempfile



@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/download')
def download():
    conn = sqlite3.connect("./app.db")
    cur = conn.cursor()
    
    cur.execute("select * from user")
    user_id = cur.fetchone()[0]
    
    cur.execute("select * from button_data where user_id = %s" % str(user_id))
    all_data = cur.fetchall()
    conn.close()
    
    return str(all_data)
        
    
    '''
    try:
        #with tempfile.NamedTemporaryFile(mode='w') as fp:
        with open('./app/data.txt','w') as fp:
            for thisData in all_data:
                fp.write(str(thisData) + '\n')
        return send_file('data.txt', attachment_filename='data.txt')
        #return render_template('download.html', title='Download', dynamic_data = 'success')
        
    except Exception as e:
        dynamic_data = str(e)
        return render_template('download.html', title='Download', dynamic_data = dynamic_data)
    '''
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)



