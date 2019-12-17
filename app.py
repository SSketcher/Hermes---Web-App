from flask import Flask, request, url_for, redirect, render_template, flash, session, logging, request, Markup
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, ValidationError
from passlib.hash import sha256_crypt
from functools import wraps
from random import sample


app = Flask(__name__)


#___MyDQL config___
app.config['MYSQL_HOST'] = 'sql7.freemysqlhosting.net'
app.config['MYSQL_USER'] = 'sql7314271'
app.config['MYSQL_PASSWORD'] = 'iGQhnDbfKa'
app.config['MYSQL_DB'] = 'sql7314271'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#___MyDQL config___
mysql = MySQL(app)


#___Creating custom valisator___

def id_check(form, field):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM HermesVN WHERE Hermes_id = %s",[field.data])
    if result > 0:
        data = cur.fetchone()
        used = data['Used']
        if used == True:
            raise ValidationError('This Hermes Id number was already used!!')
    else:
        raise ValidationError('Incorrect Hermes Id number!!')


#___Registration block___
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    last_name = StringField('Last Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Length(min=6, max=50)
    ])
    hermes_id = StringField('Hermes Id Number', [
        validators.DataRequired(),  
        id_check
    ])
    password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords don not match')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        last_name = form.last_name.data
        hermes_id = form.hermes_id.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        #___Create cursor___
        cur = mysql.connection.cursor()
        #___SQL Query___
        cur.execute("INSERT INTO users(Name, LastName, Email, UsersPassword, Hermes_id) VALUES(%s, %s, %s, %s, %s)",[name, last_name, email, password, hermes_id])
        cur.execute("UPDATE HermesVN SET used = 1 WHERE hermes_id = %s;",[hermes_id])
        #___Commit to DB___
        mysql.connection.commit()
        #___Closing connection___
        cur.close()
        return redirect(url_for('index'))
    return render_template('register_wtf.html', form = form)


#___Login block___
@app.route('/log', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']       
        
        #___Create cursor___
        cur = mysql.connection.cursor()
        #___Get User by Username___
        result = cur.execute("SELECT * FROM users WHERE email = %s",[email])

        if result > 0:
            data = cur.fetchone()
            password = data['UsersPassword']
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['user_id'] = data['UsersID']
                flash('You are now logged in','success')
                return redirect('user_home')
            else:
                error = 'Invalid password'
                return render_template('log_wtf.html', error = error)
        else:
            error = 'User not found'
            return render_template('log_wtf.html', error = error )
    return render_template('log_wtf.html')

#__Adding decorators__
def is_logged_in(f):
    @wraps(f)
    def wrap(*ards, **kwargs):
        if 'logged_in' in session:
            return f(*ards, **kwargs)
        else:
            flash('Unuthorize, log in !', 'danger')
            return redirect(url_for('log'))
    return wrap

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logout', 'message')
    return redirect(url_for('index'))


#__Subpages__
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user')
@is_logged_in
def user():
    return render_template('user.html')

@app.route('/user_home')
@is_logged_in
def user_home():
    return render_template('user_home.html')

@app.route('/user_profile')
@is_logged_in
def user_profile():
    return render_template('user_profile.html')
    
@app.route('/user_stats')
@is_logged_in
def user_stats():
    return render_template('user_stats.html')

@app.route('/heart_ratio')
@is_logged_in
def heart_ratio():
    return render_template('heart_ratio.html')

@app.route('/activity_char')
@is_logged_in
def activity_char():
    activity_data=sample(range(1,10),3)
    return render_template('activity_char.html',values=activity_data)

    
@app.route('/sleep_char')
@is_logged_in
def sleep_char():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * from chart_test")
    data = cursor.fetchall()
    sleep_data = []
    for row in data:
      sleep_data.append(row['Day1'])
      sleep_data.append(row['Day2'])
      sleep_data.append(row['Day3'])

    return render_template('sleep_char.html',values=sleep_data)

@app.route('/mind_char')
@is_logged_in
def mind_char():
    mind_data=sample(range(10,50),2)
    return render_template('mind_char.html',values=mind_data)

@app.route('/health_char')
@is_logged_in
def health_char():

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * from steps_tab")
    data = cursor.fetchall()
    health_data = []
    for row in data:
      health_data.append(row['Day1'])
      health_data.append(row['Day2'])
      health_data.append(row['Day3'])
      health_data.append(row['Day4'])
      health_data.append(row['Day5'])
      health_data.append(row['Day6'])
      health_data.append(row['Day7'])

    return render_template('health_char.html',values=health_data)


if __name__ == "__main__":
    app.secret_key = 'oliwiakrauze'
    app.run(debug = True)

