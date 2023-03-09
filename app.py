from flask import Flask, render_template, redirect, flash, request, session, abort
from database import Database
from webargs import fields
from webargs.flaskparser import use_args
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash
from exceptions import AlreadyExistError

app = Flask(__name__)

db = Database()
load_dotenv()

app.secret_key = os.getenv('SECRET_KEY', 'somesecretkey')


@app.get('/')
def index():
    return render_template('home.html')


@app.get('/register')
def register():
    return render_template('register.j2')


@app.post('/register')
@use_args({
    'business_name': fields.Str(required=True),
    'email': fields.Email(required=True),
    'password': fields.Str(required=True,)
}, location='form')
def register_post(data):
    try:
        result = db.add_user(
            data['business_name'],
            data['email'],
            generate_password_hash(data['password'])
        )
    except AlreadyExistError as e:
        flash(e.message, 'app_error')
        return redirect(request.referrer)

    print(result)
    session['user_id'] = result.id
    return redirect('/dashboard')


@app.get('/login')
def login():
    return render_template('login.j2')


@app.post('/login')
@use_args({
    'email': fields.Email(required=True),
    'password': fields.Str(required=True,)
}, location='form')
def login_post(request):
    return redirect('/')


@app.get('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect('/login')
    return render_template('auth/dashboard.html')


@app.errorhandler(422)
@app.errorhandler(400)
def handle_error(err):
    messages = err.data.get('messages', ['Invalid request.'])
    flash({'errors': messages}, 'validation_error')
    return redirect(request.referrer)
