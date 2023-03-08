from flask import Flask, render_template
app = Flask(__name__)


@app.get('/')
def index():
    return render_template('home.html')


@app.get('/register')
def register():
    return render_template('register.html')


@app.get('/login')
def login():
    return render_template('login.html')
