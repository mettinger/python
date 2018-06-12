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

from app.email import send_password_reset_email

from app import db
from app.forms import RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm

import sqlite3
import tempfile

from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html, components
from bokeh.models import Title

import datetime
import numpy as np

import matplotlib.pyplot as plt
plt.switch_backend('agg')
import seaborn as sns
sns.set()

import mpld3
import sys
from math import pi
import numpy as np

# PRINT TO CONSOLE: print(string_of_interest, file=sys.stderr)

# HELPER FUNCTIONS

def db_query_read(queryString):
    
    conn = sqlite3.connect("./app.db")
    cur = conn.cursor()
    cur.execute(queryString)
    result = cur.fetchall()
    conn.close()
    return result
    
def user_id_get(username):
    
    queryString = "select id from user where username = '%s'" % username
    user_id = db_query_read(queryString)[0][0]
    return user_id
    
def user_data_all_get(user_id):
    
    queryString = "select * from button_data where user_id = %s" % str(user_id)
    all_data = db_query_read(queryString)
    return all_data

def string_to_datetime(datetime_string):
    year,month,day,hour,minute,second,millisecond = [int(i) for i in datetime_string.split('.')]
    return datetime.datetime(*[year,month,day,hour,minute,second,millisecond * 1000])

def timedeltas(timestampData):
    datetimes = [string_to_datetime(thisTimeStamp[1]) for thisTimeStamp in timestampData]
    deltas = [(datetimes[i] - datetimes[i-1]).total_seconds() for i in range(1,len(datetimes))]
    return deltas



# ROUTES

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

@app.route('/loginApp/<data>')
def loginApp(data):
    
    username, password = data.split("-")
    try:
        user = User.query.filter_by(username=username).first()
        if not user.check_password(password):
            returnString = "Username or Password Error..."
        else:
            queryString = "select id from user where username = '%s'" % username
            userID = db_query_read(queryString)[0][0]
            returnString = str(userID)
    except:
        returnString = "Username or Password Error..."
        
    response = make_response(returnString)
    return response

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
    
@app.route('/download')
def download():
    
    user_id = user_id_get(current_user.username)
    all_data = ['timestamp, button_id, text_info'] + [str(i[1]) + ',' + str(i[2]) + ',' + str(i[4]) for i in user_data_all_get(user_id)]
      
    csv = "\n".join(all_data)
    response = make_response(csv)
    cd = 'attachment; filename=mycsv.csv'
    response.headers['Content-Disposition'] = cd 
    response.mimetype='text/csv'

    return response

@app.route('/plot')
def plot():
    
    user_id = user_id_get(current_user.username)
    results = user_data_all_get(user_id)
    
    if len(results) == 0:
        return "No data yet...";
    
    deltas = timedeltas(results)
    time_points = [0] + list(np.cumsum(deltas))
    
    timeStrings = [i[1] for i in results]
    
    colors = ["blue" if i[2] == 0 else "red" for i in results]
    plot = figure()
    for i in range(len(time_points)):
        this_sec = time_points[i]
        this_color = colors[i]
        
        plot.line([this_sec, this_sec], [0,1], line_color=this_color)
        plot.circle([this_sec, this_sec], [0,1], fill_color=this_color, line_color=this_color, size=6)
    
    a = time_points
    plot.xaxis.ticker = a
    plot.xaxis.major_label_overrides = {a[i]:timeStrings[i] for i in range(len(a))}
    #p.xaxis.major_label_overrides = {1: 'A', 2: 'B', 3: 'C'}
    
    
    plot.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    plot.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
    
    plot.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels
    
    plot.xaxis.major_label_orientation = -pi/4

    plot.background_fill_color = "LightGrey"
    plot.background_fill_alpha = 0.2
    
    plot.xaxis.axis_label = "Timestamp"
    
    #plot.add_layout(Title(text="      Try ZOOM for a closer look."), 'above')
    plot.add_layout(Title(text="Tip: Timestamps on the x-axis may be overlapping and messy.  Try ZOOM for a closer look."), 'above')
    plot.add_layout(Title(text="Events: Blue = Button 0, Red = Button 1 ",text_font_size="16pt"), 'above')

    script, div = components(plot)

    return render_template("plot.html", the_div=div, the_script=script)

    

@app.route('/plot_old')
def plot_old():
    
    user_id = user_id_get(current_user.username)
    results = user_data_all_get(user_id)
    
    deltas = timedeltas(results)
    time_points = np.cumsum(deltas)
    
    colors = ["blue" if i[2] == 0 else "red" for i in results[1:]]
    plot = figure(title="Events: Blue = Button 0, Red = Button 1")
    for i in range(len(time_points)):
        this_sec = time_points[i]
        this_color = colors[i]
        
        plot.line([this_sec, this_sec], [0,1], line_color=this_color)
        plot.circle([this_sec, this_sec], [0,1], fill_color=this_color, line_color=this_color, size=6)
        
    plot.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    plot.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
    
    plot.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels

    plot.background_fill_color = "LightGrey"
    plot.background_fill_alpha = 0.2
    
    plot.xaxis.axis_label = "Seconds from first button event"
    
    script, div = components(plot)

    return render_template("plot.html", the_div=div, the_script=script)

    #html = file_html(plot, CDN, "my plot")
    #return html
    
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/install_android_app')
def installAndroidApp():
     return send_file('/home/ubuntu/github/python/buttonApp_2/app/static/app-release.apk', as_attachment=True)
        
        
        
        




