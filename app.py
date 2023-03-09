from flask import Flask, render_template, redirect, flash, request, session
from database import Database
from webargs import fields
from webargs.flaskparser import use_args
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash, check_password_hash
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
def login_post(data):
    user = db.fetch_user(data['email'])
    is_password_valid = check_password_hash(
        user.password if user else '',
        data['password']
    )
    if not user or not is_password_valid:
        flash('Invalid email address or password.', 'app_error')
        return redirect(request.referrer)
    session['user_id'] = user.id
    return redirect('/dashboard')


@app.get('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    (
        (total_products, products_out_of_stock),
        (total_categories, empty_categories)
    ) = db.fetch_products_and_categories_count(user_id)

    return render_template(
        'auth/dashboard.html',
        total_products=total_products,
        products_out_of_stock=products_out_of_stock,
        total_categories=total_categories,
        empty_categories=empty_categories
    )


@app.get('/categories')
def categories():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    categories = db.fetch_categories(user_id)
    return render_template(
        'auth/categories.html',
        categories=enumerate(categories)
    )


@app.post('/categories')
@use_args({
    'name': fields.Str(required=True, validate=lambda x: len(x) > 1),
}, location='form')
def categories_post(data):
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    try:
        db.add_category(data['name'], user_id)
    except AlreadyExistError as e:
        flash(e.message, 'app_error')
        return redirect(request.referrer)
    flash('Category added successfully.', 'success')
    return redirect(request.referrer)


@app.post('/categories/<id>')
def categories_delete(id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    try:
        db.delete_category(int(id), user_id)
    except Exception:
        flash('Unable to delete. Please try again.', 'app_error')
        return redirect(request.referrer)
    flash('Category deleted successfully.', 'success')
    return redirect(request.referrer)


@app.get('/products')
def products():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    categories = db.fetch_categories(user_id)
    return render_template(
        'auth/products.html',
        categories=categories
    )


@ app.post('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


@ app.errorhandler(422)
@ app.errorhandler(400)
def handle_error(err):
    messages = err.data.get('messages', ['Invalid request.'])
    flash({'errors': messages}, 'validation_error')
    return redirect(request.referrer)
