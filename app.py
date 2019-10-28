from flask import Flask, request, url_for, redirect, render_template



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        return redirect(url_for('index'))

    return render_template('log.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return redirect(url_for('register'))

    return render_template('register.html')


if __name__ == "__main__":
    app.run(debug = True)