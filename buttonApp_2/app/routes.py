from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from app.models import User

from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from flask import send_file, make_response

from flask import request
from werkzeug.urls import url_parse

from app import db
from app.forms import RegistrationForm

import sqlite3
import tempfile

from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.mpl import to_bokeh

import datetime
import numpy as np

import matplotlib.pyplot as plt
plt.switch_backend('agg')
import seaborn as sns
sns.set()

import mpld3



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

def user_id_get(username):
    
    conn = sqlite3.connect("./app.db")
    cur = conn.cursor()
    cur.execute("select * from user where username = '%s'" % username)
    user_id = cur.fetchone()[0]
    conn.close()
    return user_id
    
def user_data_all_get(user_id):
    
    conn = sqlite3.connect("./app.db")
    cur = conn.cursor()
    cur.execute("select * from button_data where user_id = %s" % str(user_id))
    all_data = cur.fetchall()
    conn.close()
    return all_data
    
@app.route('/download')
def download():
    
    user_id = user_id_get(current_user.username)
    all_data = [str(i) for i in user_data_all_get(user_id)]
      
    csv = "\n".join(all_data)
    response = make_response(csv)
    cd = 'attachment; filename=mycsv.csv'
    response.headers['Content-Disposition'] = cd 
    response.mimetype='text/csv'

    return response

def string_to_datetime(datetime_string):
    year,month,day,hour,minute,second,millisecond = [int(i) for i in datetime_string.split('.')]
    return datetime.datetime(*[year,month,day,hour,minute,second,millisecond * 1000])

def timedeltas(timestampData):
    datetimes = [string_to_datetime(thisTimeStamp[1]) for thisTimeStamp in timestampData]
    deltas = [(datetimes[i] - datetimes[i-1]).total_seconds() for i in range(1,len(datetimes))]
    return deltas

@app.route('/plot')
def plot():
    
    user_id = user_id_get(current_user.username)
    results = user_data_all_get(user_id)
    
    deltas = timedeltas(results)
    time_points = np.cumsum(deltas)
    
    x = [0]
    y = [0]
    for i in time_points:
        x.extend([i,i,i])
        y.extend([0,1,0])
    
    fig = plt.figure()
    plt.plot(x,y,'-')
    
    html = mpld3.fig_to_html(fig)
    #plot = to_bokeh(fig)
    #html = file_html(plot, CDN, "my plot")
    return html
    




