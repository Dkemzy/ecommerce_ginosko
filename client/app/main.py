from flask import Flask, Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from forms import LoginForm, AddProductForm, RegistrationForm, LoginForm, EditUserForm, CustomerProfileForm, ChangeUserRoleForm, EditProductForm
from models import db, User, Product, Order, NewsArticle, OrderItem
from werkzeug.utils import secure_filename
from sqlalchemy import func
import os

main = Blueprint('main', __name__)

bcrypt = Bcrypt()


# Route to render the index page
@main.route('/')
def index():
    # Fetch random products from the database using your Product model
    # Adjust the query as needed based on your database model and requirements
    products = Product.query.order_by(func.random()).limit(3).all()

    # Render the index template with the fetched products
    return render_template('index.html', products=products)

@main.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    # Fetch products from the database using your Product model
    products = Product.query.all()

    # Create an instance of the AddProductForm
    add_product_form = AddProductForm()

    # Handle the form submission for adding a new product
    if add_product_form.validate_on_submit():
        name = add_product_form.name.data
        price = add_product_form.price.data
        details = add_product_form.details.data
        image = add_product_form.image.data

        # Handle file upload and create a new product
        if image:
            filename = secure_filename(image.filename)
            file_path = os.path.join(os.getcwd(), 'uploads', filename)
            image.save(file_path)
        else:
            file_path = None

        new_product = Product(name=name, price=price, details=details, image=file_path)

        # Add the new product to the database
        db.session.add(new_product)
        
        try:
            db.session.commit()
            flash('Product added successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error adding product. Please try again.', 'danger')

        # Redirect to the product management page
        return redirect(url_for('main.products'))

    # Render the product management page with products and the form
    return render_template('products.html', products=products, form=add_product_form)

@main.route('/api/products', methods=['GET'])
def get_all_products():
    # Fetch all products from the database
    products = Product.query.all()

    # Pagination logic (adjust as needed)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    paginated_products = products.paginate(page=page, per_page=per_page)

    # Convert products to a list of dictionaries for easy serialization
    product_list = [
        {'id': product.id, 'name': product.name, 'price': product.price, 'details': product.details}
        for product in paginated_products.items
    ]

    # Add pagination information to the response
    pagination_info = {
        'total_pages': paginated_products.pages,
        'total_items': paginated_products.total,
        'current_page': paginated_products.page,
        'per_page': paginated_products.per_page,
        'next_page': url_for('main.get_all_products', page=paginated_products.next_num, per_page=per_page) if paginated_products.has_next else None,
        'prev_page': url_for('main.get_all_products', page=paginated_products.prev_num, per_page=per_page) if paginated_products.has_prev else None,
    }

    response = {'products': product_list, 'pagination': pagination_info}

    return jsonify(response)

# Define a route for retrieving a specific product by ID
@main.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    # Fetch the product from the database by ID
    product = Product.query.get_or_404(product_id)

    # Convert the product to a dictionary for serialization
    product_data = {'id': product.id, 'name': product.name, 'price': product.price, 'details': product.details}

    return jsonify(product_data)

# Define a route for adding a new product
@main.route('/api/products', methods=['POST'])
def add_product():
    form = AddProductForm()

    if form.validate_on_submit():
        # Access form data using form.name.data, form.price.data, etc.
        name = form.name.data
        price = form.price.data
        details = form.details.data
        image = form.image.data

        # Handle file upload
        if image:
            # Securely save the uploaded file
            filename = secure_filename(image.filename)
            file_path = os.path.join('uploads', filename)  # 'uploads' is a folder in your project
            image.save(file_path)
        else:
            file_path = None

        # Create a new product
        new_product = Product(name=name, price=price, details=details, image=file_path)

        # Add the new product to the database
        db.session.add(new_product)

        try:
            db.session.commit()
            # Return the added product data
            return jsonify({
                'id': new_product.id,
                'name': new_product.name,
                'price': new_product.price,
                'details': new_product.details,
                'image': new_product.image
            }), 201
        except Exception as e:
            db.session.rollback()
            # Remove the uploaded file if the commit fails
            if file_path:
                os.remove(file_path)
            return jsonify({'error': 'Error adding product to the database'}), 500

    # If form validation fails, return the errors
    errors = {field.name: field.errors for field in form}
    return jsonify({'error': 'Form validation failed', 'errors': errors}), 400

# Define a route for updating an existing product
@main.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = EditProductForm(obj=product)

    if form.validate_on_submit():
        # Update product information based on the form data
        product.name = form.name.data
        product.price = form.price.data
        product.details = form.details.data

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('main.products'))

    return render_template('edit_product.html', form=form, product=product)

@main.route('/delete_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        # Handle the delete logic here
        db.session.delete(product)
        db.session.commit()

        flash('Product deleted successfully!', 'success')
        return redirect(url_for('main.products'))

    return render_template('confirm_delete_product.html', product=product)

@main.route('/support')
def support_page():
    return render_template('support.html')


@main.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # Use the RegistrationForm for handling the registration form

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('main.register'))

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists. Please choose another one.', 'danger')
            return redirect(url_for('main.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful for {}!'.format(username), 'success')
        login_user(new_user)
        return redirect(url_for('main.index'))

    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Use the LoginForm for handling the login form

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html', form=form)


@main.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    # Ensure that only superusers can access this route
    if current_user.role != 'superuser':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    # Fetch all users from the database
    users = User.query.all()

    # Handle changing user roles
    change_role_form = ChangeUserRoleForm()

    if change_role_form.validate_on_submit():
        user_id = change_role_form.data['user_id']
        new_role = change_role_form.data['role']

        user = User.query.get_or_404(user_id)
        user.role = new_role

        db.session.commit()

        flash(f'Role changed for {user.username}!', 'success')
        return redirect(url_for('main.manage_users'))

    return render_template('manage_users.html', users=users, change_role_form=change_role_form)

@main.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    # Ensure that only superusers can access this route
    if current_user.role != 'superuser':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        # Update user information based on the form data
        user.username = form.username.data
        user.email = form.email.data
        # Add more fields as needed

        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('main.manage_users'))

    return render_template('edit_user.html', form=form, user=user)

@main.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    # Ensure that only superusers can access this route
    if current_user.role != 'superuser':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Handle the delete logic here
        db.session.delete(user)
        db.session.commit()

        flash('User deleted successfully!', 'success')
        return redirect(url_for('main.manage_users'))

    # For a GET request, render a confirmation template
    return render_template('confirm_delete_user.html', user=user)
    
@main.route('/change_user_role/<int:user_id>', methods=['GET', 'POST'])
@login_required
def change_user_role(user_id):
    # Ensure that only superusers can access this route
    if current_user.role != 'superuser':
        flash('You do not have permission to change user roles.', 'danger')
        return redirect(url_for('main.index'))

    # Fetch the user from the database
    user = User.query.get_or_404(user_id)

    # Create an instance of the ChangeUserRoleForm
    form = ChangeUserRoleForm(obj=user)

    if form.validate_on_submit():
        # Update the user role based on the form data
        user.role = form.data['role']

        # Commit the changes to the database
        db.session.commit()

        flash(f'Role changed for {user.username}!', 'success')
        return redirect(url_for('main.manage_users'))

    # Render the template with the form
    return render_template('change_user_role.html', form=form, user=user)

@main.route('/admin_dashboard')
@login_required  # Ensure that only logged-in admins can access the dashboard
def admin_dashboard():
    # Render the admin dashboard template
    return render_template('admin_dashboard.html')

@main.route('/superuser_dashboard')
@login_required
def superuser_dashboard():
    # Your logic for the superuser dashboard goes here
    return render_template('superuser_dashboard.html')

@main.route('/orders')
@login_required
def display_orders():
    # Assuming you retrieve orders from the database, you might do something like this:
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)

@main.route('/basket')
@login_required
def basket_page():
    # Fetch basket items from the database for the current user
    user_basket = get_user_basket(current_user)

    return render_template('basket.html', basket=user_basket)

# Helper function to get basket items for the current user
def get_user_basket(user):
    # Assuming you have a relationship between User and Order in your models
    user_orders = Order.query.filter_by(customer_name=user.username).all()

    # Assuming one user can have multiple orders
    # You may need to adjust this logic based on your application's structure
    user_basket = []

    for order in user_orders:
        for item in order.items:
            product_info = {
                'name': item.product_name,
                'quantity': item.quantity,
                'total_price': item.price * item.quantity,
                'image': item.product.image  # Assuming you have an 'image' field in your Product model
            }
            user_basket.append(product_info)

    return user_basket


@main.route('/add_to_basket', methods=['POST'])
@login_required
def add_to_basket():
    if request.method == 'POST':
        data = request.get_json()

        # Extract relevant data from the request
        product_name = data.get('name')
        product_price = data.get('price')
        product_image = data.get('image')

        # Assuming you have a relationship between User and Order in your models
        user_order = Order.query.filter_by(customer_name=current_user.username, status='active').first()

        if not user_order:
            # Create a new order for the user if they don't have an active order
            user_order = Order(customer_name=current_user.username, status='active')
            db.session.add(user_order)
            db.session.commit()

        # Add the product to the order items
        order_item = OrderItem(
            product_name=product_name,
            price=product_price,
            quantity=1,  # You can adjust the quantity as needed
            order=user_order
        )

        db.session.add(order_item)
        db.session.commit()

        return jsonify({'message': 'Product added to the basket successfully'})

    return jsonify({'error': 'Invalid request method'})

@main.route('/checkout')
def checkout():
    # Fetch order details from the database
    order = get_order_details()  # Replace this with your logic to get order details

    return render_template('checkout.html', order=order)

# Helper function to get order details (replace it with your actual logic)
def get_order_details():
    # Assuming you have a user or some way to identify the current user
    user_id = get_current_user_id()  # Replace this with your logic to get the user ID
    
    # Fetch the latest order for the current user
    order = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).first()

    if order:
        # Fetch order items for the order
        order_items = OrderItem.query.filter_by(order_id=order.id).all()

        # Prepare the order dictionary
        order_details = {
            'items': [
                {
                    'name': item.product_name,
                    'quantity': item.quantity,
                    'total_price': item.price * item.quantity
                }
                for item in order_items
            ],
            'total_price': order.total_price,
        }

        return order_details

    return None

# Helper function to get the current user ID (replace it with your actual logic)
def get_current_user_id():
    # Replace this with your logic to get the current user ID
    # For demonstration purposes, let's assume you have a user object
    # and you are using Flask-Login
    if current_user.is_authenticated:
        return current_user.id
    return None


@main.route('/customer')
def customer_page():
    # Fetch products from the database using your Product model
    products = Product.query.all()

    # Convert product objects to a list of dictionaries for easy rendering in the template
    product_list = [
        {'name': product.name, 'price': product.price, 'details': product.details, 'image': product.image}
        for product in products
    ]

    return render_template('customer.html', products=product_list)


@main.route('/customer_profile', methods=['GET', 'POST'])
def customer_profile():
    form = CustomerProfileForm()

    if request.method == 'POST' and form.validate_on_submit():
        # Process the form data (update the profile) here
        current_user.username = form.customer_name.data
        current_user.email = form.customer_email.data
        current_user.location = form.customer_location.data
        db.session.commit()

        # Redirect to a success page or the profile page
        return redirect(url_for('main.customer_profile'))

    # Pass the current user's information to pre-fill the form
    form.customer_name.data = current_user.username
    form.customer_email.data = current_user.email
    form.customer_location.data = current_user.location

    return render_template('customer_profile.html', form=form)

@main.route('/create_news', methods=['GET', 'POST'])
@login_required
def create_news():
    if request.method == 'POST':
        # Handle the form submission here
        news_title = request.form.get('news_title')
        news_summary = request.form.get('news_summary')
        news_content = request.form.get('news_content')

        # Create a new NewsArticle instance
        new_article = NewsArticle(
            title=news_title,
            summary=news_summary,
            content=news_content,
            user_id=current_user.id  # Set the user_id using the current user's ID
        )

        # Save the news article to the database
        db.session.add(new_article)
        db.session.commit()

        # Redirect to the news page after submitting the article
        return redirect(url_for('main.news'))

    # Render the create news page
    return render_template('create_news.html')

@main.route('/news')
def news():
    # Fetch news articles from the database
    news_articles = NewsArticle.query.all()

    # Render the news template with the fetched articles
    return render_template('news.html', news_articles=news_articles)

@main.route('/article/<int:article_id>')
def article_detail(article_id):
    # Fetch the article from the database using the article_id
    article = NewsArticle.query.get_or_404(article_id)

    # Print the content to the console for debugging
    print(article.content)

    # Render the article_detail template with the article data
    return render_template('article_detail.html', article=article)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Error in the {getattr(form, field).label.text} field - {error}', 'danger')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
