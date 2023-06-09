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

app.secret_key = os.getenv('SECRET_KEY', 'some-secret-key')


@app.get('/')
def index():
    return render_template('home.html')


@app.get('/register')
def register():
    if session.get('user_id'):
        return redirect('/dashboard')
    return render_template('register.html')


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

    session['user_id'] = result.id
    return redirect('/dashboard')


@app.get('/login')
def login():
    if session.get('user_id'):
        return redirect('/dashboard')
    return render_template('login.html')


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
    if categories:
        categories = enumerate(categories)

    return render_template(
        'auth/categories.html',
        categories=categories
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


@app.get('/categories/edit/<id>')
def categories_edit(id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    category = db.fetch_category(user_id, id)
    return render_template(
        'auth/categories-edit.html',
        category=category
    )


@app.post('/categories/edit/<id>')
@use_args({
    'name': fields.Str(required=True, validate=lambda x: len(x) > 1),
}, location='form')
def categories_put(data, id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    try:
        db.update_category(int(id), data['name'], user_id)
    except AlreadyExistError as e:
        flash(e.message, 'app_error')
        return redirect(request.referrer)
    flash('Category updated successfully.', 'success')
    return redirect(request.referrer)


@app.post('/categories/delete/<id>')
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

    products = db.fetch_products(user_id)
    if products:
        products = enumerate(products)

    categories = db.fetch_categories(user_id)
    return render_template(
        'auth/products.html',
        products=products,
        categories=categories
    )


@app.post('/products')
@use_args({
    'name': fields.Str(required=True, validate=lambda x: len(x) > 1),
    'price': fields.Int(required=True),
    'quantity': fields.Int(required=True),
    'category_id': fields.Int(required=True)
}, location='form')
def products_post(data):

    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    category = db.fetch_category(user_id, data['category_id'])
    if not category:
        flash({'errors': {
            'form': {'category_id': ['The category does not exist']}
        }}, 'validation_error')
        return redirect(request.referrer)

    try:
        db.add_product(
            data['name'],
            data['price'],
            data['quantity'],
            data['category_id'],
            user_id
        )
    except AlreadyExistError as e:
        flash(e.message, 'app_error')
        return redirect(request.referrer)
    flash('Product added successfully.', 'success')
    return redirect(request.referrer)


@app.get('/products/edit/<id>')
def products_edit(id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    product = db.fetch_product(user_id, id)
    categories = db.fetch_categories(user_id)

    if not product:
        return redirect('/products')

    return render_template(
        'auth/products-edit.html',
        product=product,
        categories=categories,
    )


@app.post('/products/edit/<id>')
@use_args({
    'name': fields.Str(required=True, validate=lambda x: len(x) > 1),
    'price': fields.Float(required=True),
    'quantity': fields.Int(required=True),
    'category_id': fields.Int(required=True)
}, location='form')
def product_put(data, id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    category = db.fetch_category(user_id, data['category_id'])
    if not category:
        flash({'errors': {
            'form': {'category_id': ['The category does not exist']}
        }}, 'validation_error')
        return redirect(request.referrer)

    try:
        db.update_product(
            int(id),
            data['name'],
            data['price'],
            data['quantity'],
            data['category_id'],
            user_id
        )
    except AlreadyExistError as e:
        flash(e.message, 'app_error')
        return redirect(request.referrer)
    flash('Product updated successfully.', 'success')
    return redirect(request.referrer)


@app.post('/products/delete/<id>')
def products_delete(id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    try:
        db.delete_product(int(id), user_id)
    except Exception:
        flash('Unable to delete. Please try again.', 'app_error')
        return redirect(request.referrer)
    flash('Product deleted successfully.', 'success')
    return redirect(request.referrer)


@app.post('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


@app.errorhandler(422)
@app.errorhandler(400)
def handle_error(err):
    messages = err.data.get('messages', ['Invalid request.'])
    flash({'errors': messages}, 'validation_error')
    return redirect(request.referrer)
