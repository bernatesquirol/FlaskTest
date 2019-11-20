from flask import Flask, request, render_template, abort, redirect, url_for, jsonify
from flask_pymongo import PyMongo
import bson
from bson.objectid import ObjectId
from fooApp.forms import ProductForm, LoginForm
from fooApp.models import User

from flask_login import LoginManager, current_user, login_required
from flask_login import login_user, logout_user
a1b2c3d4
app = Flask(__name__, template_folder='templates', static_folder='static')

app.config['MONGO_DBNAME'] = 'foodb'
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/foodb'
app.config['MONGO_URI'] = 'mongodb+srv://bernat:a1b2c3d4@cluster0-me4ti.mongodb.net/test?retryWrites=true&w=majority'

app.config['SECRET_KEY'] = 'sLgz46L6SAfy4MDtAxpdz1bKtO37H728'
app.config['SESSION_PROTECTION'] = 'strong'

mongo = PyMongo(app)
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    u = mongo.db.users.find_one({"username": user_id})
    if not u:
        return None
    return User(u['username'])


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('products_list'))
    form = LoginForm(request.form)
    error = None
    if request.method == 'POST' and form.validate():
        user = mongo.db.users.find_one({"username": form.username.data})
        if user and User.validate_login(user['password'], form.password.data):
            login_user(User(user['username']))
            return redirect(url_for('products_list'))
        else:
            error = 'Incorrect username or password.'
    return render_template('user/login.html', form=form, error=error)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('products_list'))


@app.route('/')
def index():
    return redirect(url_for('products_list'))


@app.errorhandler(404)
def error_not_found(error):
    return render_template('error/not_found.html'), 404


@app.errorhandler(bson.errors.InvalidId)
def error_not_found(error):
    return render_template('error/not_found.html'), 404


@app.route('/products/')
@login_required
def products_list():
    products = mongo.db.products.find()[:]
    return render_template('product/index.html', products=products)


@app.route('/products/<product_id>/')
@login_required
def product_detail(product_id):
    prod = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    if prod is None:
        abort(404)
    return render_template('product/detail.html', product=prod)


@app.route('/products/<product_id>/edit/', methods=['GET', 'POST'])
@login_required
def product_edit(product_id):
    prod = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    form = ProductForm(request.form)
    if form.validate():
        mongo.db.products.replace_one(prod, {'name': form.name.data, 'description': form.description.data, 'price': form.price.data})
        return redirect('/')

    return render_template('product/edit.html', product=prod, form=form)


@app.route('/products/<product_id>/delete/', methods=['DELETE'])
@login_required
def product_delete(product_id):
    result = mongo.db.products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        response = jsonify({'status': 'Not Found'})
        response.status = 404
        return response
    return jsonify({'status': 'OK'})


@app.route('/products/create/', methods=['GET', 'POST'])
@login_required
def product():
    form = ProductForm(request.form)
    if form.validate():
        mongo.db.products.insert_one({'name': form.name.data, 'description': form.description.data, 'price': form.price.data})
        return redirect('/')
    return render_template('product/create.html', form=form)


if __name__ == '__main__':
    app.run()
