
import os
from flask import Flask, render_template, redirect, url_for, request, flash, session, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DecimalField, FileField
from wtforms.validators import DataRequired, Length, Email, ValidationError


app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024


db = SQLAlchemy(app)


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    products = db.relationship('Product', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=20)
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        Length(min=6)
    ])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered')

    def validate_confirm_password(self, confirm_password):
        if self.password.data != confirm_password.data:
            raise ValidationError('Passwords must match')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = DecimalField('Price', places=2, validators=[DataRequired()])
    description = TextAreaField('Description')
    image = FileField('Product Image')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in {'png', 'jpg', 'jpeg'}



@app.route('/')
def home():
    if "user_id" not in session:
       return render_template("main.html")
    products = Product.query.all()
    return render_template('home.html', products=products)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', category="success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash("You logged in successfully!", category="success")
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', category="danger")
    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You logged out", category="success")
    return redirect(url_for('home'))


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    form = ProductForm()
    if form.validate_on_submit():
        file = form.image.data
        filename = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        product = Product(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            image=filename,
            user_id=session['user_id']
        )
        db.session.add(product)
        db.session.commit()
        flash("You added a new product successfully!", category="success")
        return redirect(url_for('dashboard'))

    return render_template('product_form.html', form=form)


@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    if product.user_id != session.get('user_id'):
        return redirect(url_for('home'))

    form = ProductForm(obj=product)
    if form.validate_on_submit():
        form.populate_obj(product)

        file = form.image.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image = filename

        db.session.commit()
        flash("You edited the product successfully!", category="success")
        return redirect(url_for('dashboard'))

    return render_template('product_form.html', form=form)


@app.route('/delete_product/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    if product.user_id != session.get('user_id'):
        return redirect(url_for('home'))

    db.session.delete(product)
    db.session.commit()
    flash("You deleted the product successfully!", category="success")
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)