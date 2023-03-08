from flask import Flask, render_template, redirect, jsonify, flash, request
from webargs import fields, validate
from webargs.flaskparser import use_args
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

app.secret_key = os.getenv('SECRET_KEY', 'somesecretkey')


@app.get('/')
def index():
    return render_template('home.html')


@app.get('/register')
def register():
    return render_template('register.html')


@app.post('/register')
@use_args({
    'business_name': fields.Str(required=True),
    'email': fields.Email(required=True),
    'password': fields.Str(required=True,)
}, location='form')
def register_post(request):
    return redirect('/')


@app.get('/login')
def login():
    return render_template('login.html')


@app.post('/login')
@use_args({
    'email': fields.Email(required=True),
    'password': fields.Str(required=True,)
}, location='form')
def login_post(request):
    return redirect('/')


@app.errorhandler(422)
@app.errorhandler(400)
def handle_error(err):
    messages = err.data.get('messages', ['Invalid request.'])
    flash({'errors': messages})
    return redirect(request.referrer)
