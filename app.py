from flask import Flask, request, url_for, redirect, render_template, flash, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt


app = Flask(__name__)


#___MyDQL config___
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'hermes_web_aplication'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#___MyDQL config___
mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('index.html')


#___Login block___

@app.route('/log', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        #___Create cursor___
        cur = mysql.connection.cursor()
        #___Get User by Username___
        result = cur.execute("SELECT * FROM users WHERE username = %s",(username))

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                app.logger.info('PASSWORD MATCHED')

        else:
            app.logger.info('USER NOT FOUND')

        return redirect(url_for('index'))

    return render_template('log_wtf.html')


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
        cur.execute("INSERT INTO Users(_name_, UserEmail, UserName, UserPassword) VALUES(%s, %s, %s, %s)",(name, email, username, password))
        #___Commit to DB___
        mysql.connection.commit()
        #___Closing connection___
        cur.close()

        return redirect(url_for('log_wtf'))

    return render_template('register_wtf.html', form = form)


if __name__ == "__main__":
    app.run(debug = True)