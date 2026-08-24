from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Product, CartItem, Order, OrderItem, Coupon
import os
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'store.db')
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------- AUTH ----------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('products'))
        flash('Invalid username or password', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ---------- PRODUCTS ----------

@app.route('/')
@app.route('/products')
def products():
    category = request.args.get('category')
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    all_products = query.all()
    categories = db.session.query(Product.category).distinct().all()
    return render_template('products.html', products=all_products, categories=[c[0] for c in categories])


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)


# ---------- CART ----------

@app.route('/cart')
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in items)
    return render_template('cart.html', items=items, total=total)


@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))

    if quantity < 1:
        flash('Quantity must be at least 1', 'error')
        return redirect(url_for('product_detail', product_id=product_id))

    if quantity > product.stock:
        flash(f'Only {product.stock} in stock', 'error')
        return redirect(url_for('product_detail', product_id=product_id))

    existing = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing:
        existing.quantity += quantity
    else:
        db.session.add(CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity))

    db.session.commit()
    flash('Added to cart', 'success')
    return redirect(url_for('cart'))


@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        return redirect(url_for('cart'))

    quantity = int(request.form.get('quantity', 1))
    if quantity < 1:
        db.session.delete(item)
    else:
        item.quantity = quantity
    db.session.commit()
    return redirect(url_for('cart'))


@app.route('/cart/remove/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('cart'))


# ---------- CHECKOUT ----------

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('cart'))

    subtotal = sum(item.product.price * item.quantity for item in items)
    discount = 0
    coupon_code = None

    if request.method == 'POST':
        coupon_code = request.form.get('coupon_code', '').strip()
        if coupon_code:
            coupon = Coupon.query.filter_by(code=coupon_code, active=True).first()
            if coupon:
                discount = subtotal * (coupon.discount_percent / 100)
            else:
                flash('Invalid or expired coupon code', 'error')
                return render_template('checkout.html', items=items, subtotal=subtotal, discount=0, total=subtotal)

        total = subtotal - discount

        # verify stock again before committing (race condition guard)
        for item in items:
            if item.quantity > item.product.stock:
                flash(f'{item.product.name} no longer has enough stock', 'error')
                return redirect(url_for('cart'))

        order = Order(user_id=current_user.id, total=total, coupon_code=coupon_code, status="Placed")
        db.session.add(order)
        db.session.flush()  # get order.id before commit

        for item in items:
            db.session.add(OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.product.price
            ))
            item.product.stock -= item.quantity
            db.session.delete(item)

        db.session.commit()
        flash('Order placed successfully', 'success')
        return redirect(url_for('orders'))

    return render_template('checkout.html', items=items, subtotal=subtotal, discount=discount, total=subtotal - discount)


# ---------- ORDERS ----------

@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)


@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access to this order', 'error')
        return redirect(url_for('orders'))
    return render_template('orders.html', orders=[order])


# ---------- ADMIN ----------

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('products'))

    if request.method == 'POST':
        product = Product(
            name=request.form['name'],
            category=request.form['category'],
            description=request.form.get('description', ''),
            price=float(request.form['price']),
            stock=int(request.form['stock'])
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added', 'success')

    all_products = Product.query.all()
    return render_template('admin.html', products=all_products)


# ---------- JSON API (for Playwright API-level assertions later) ----------

@app.route('/api/cart/count')
@login_required
def cart_count():
    count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'count': count})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)