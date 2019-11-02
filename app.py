from flask import Flask, request, url_for, redirect, render_template, flash, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)


#___MyDQL config___
app.config['MYSQL_HOST'] = 'sql7.freemysqlhosting.net'
app.config['MYSQL_USER'] = 'sql7310443'
app.config['MYSQL_PASSWORD'] = 'zIpZ79LfA5'
app.config['MYSQL_DB'] = 'sql7310443'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#___MyDQL config___
mysql = MySQL(app)


#___Registration block___
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
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
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        #___Create cursor___
        cur = mysql.connection.cursor()
        #___SQL Query___
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",(name, email, username, password))
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
        username = request.form['username']
        password_candidate = request.form['password']       
        
        #___Create cursor___
        cur = mysql.connection.cursor()
        #___Get User by Username___
        result = cur.execute("SELECT * FROM users WHERE username = %s",[username])

        if result > 0:
            data = cur.fetchone()
            password = data['password']
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in','success')
                return redirect('user')
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

if __name__ == "__main__":
    app.secret_key = 'oliwiakrauze'
    app.run(debug = True)