from flask import render_template, request, redirect, url_for, flash, abort, session, jsonify
import os
from .models import Cart, User, Mugs
from .forms import SignUpForm, SignInForm, UpdateForm, AddMugsForm, MakeAdminForm
from Site import app, db
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

loginmanager = LoginManager(app)

loginmanager.login_view = 'login'

img_dir = '/img/'
BASE_DIR = os.path.curdir + '/site/static/img/'
app.config['UPLOAD_DIR'] = BASE_DIR


def check_and_delete_mugs():
    mugs = Mugs.query.filter(Mugs.quantity <= 0).all()
    for mug in mugs:
        db.session.delete(mug)
    db.session.commit()


@loginmanager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


@app.route('/', methods=["GET", "POST"])
def mugs():
    check_and_delete_mugs()

    mugs = Mugs.query.all()
    return render_template('home.html', mugs=mugs)


@app.before_request
def before_request():
    if request.endpoint == 'mugs':
        check_and_delete_mugs()


@app.route('/<int:mug_id>', methods=["GET"])
def getMug(mug_id):
    mug = Mugs.query.get(mug_id)
    return render_template('singlemug.html', mug=mug)


@login_required
@app.route("/panel/cart", methods=["POST", "GET"])
def cart():
    user_id = current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    mugs = []
    final_total = 0
    for item in cart_items:
        mug = Mugs.query.get(item.mug_id)
        print(item.quantity)
        mug.quantity = item.quantity
        final_total += mug.price * mug.quantity
        mugs.append(mug)
        print(mugs)

    return render_template('cart.html', cart=mugs, final_total=final_total)


@app.route('/<int:mug_id>/add_to_cart', methods=["POST", "GET"])
def add_to_cart(mug_id):
    if current_user.is_authenticated:
        user_id = current_user.id
        cart_item = Cart.query.filter_by(mug_id=mug_id, user_id=user_id).first()
        counter = Mugs.query.get(mug_id)
        c = counter.quantity
        if cart_item:
            if c > cart_item.quantity:
                c -= 1
                cart_item.quantity += 1
                cart_item.saveToDB()
            else:
                flash('product out of stock', category='danger')
                return redirect(url_for('mugs'))
        else:
            cart = Cart(mug_id=mug_id, user_id=user_id, quantity=1)
            cart.saveToDB()

    else:
        flash('You need to log in to add items to your cart', category='danger')
        return redirect(url_for('login'))
    return redirect(url_for('cart'))


@app.route('/panel/cart/<int:mug_id>/remove', methods=["POST", "GET"])
def remove_from_cart(mug_id):
    user_id = current_user.id
    cart_item = Cart.query.filter_by(mug_id=mug_id, user_id=user_id).first()

    if not cart_item:
        return redirect(url_for('cart'))

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.saveToDB()
    else:
        cart_item.deleteFromDB()

    return redirect(url_for('cart'))


@app.route('/panel/cart/clear', methods=["POST", "GET"])
def clear_cart():
    user_id = current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    for cart_item in cart_items:
        cart_item.deleteFromDB()

    return redirect(url_for('cart'))


@app.route('/panel/cart/buy', methods=["POST", "GET"])
def buy():
    user_id = current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    for item in cart_items:
        mug = Mugs.query.get(item.mug_id)
        print(item.quantity)
        mug.update_quantity(item.quantity)
        item.deleteFromDB()

    return redirect(url_for('cart'))


@app.route("/<int:mug_id>/delete", methods=["POST", "GET"])
def deleteMug(mug_id):
    mug = Mugs.query.get(mug_id)
    mug.deleteFromDB()
    return redirect(url_for('inventory'))


@app.route("/panel/inventory", methods=["POST", "GET"])
def inventory():
    mugs = Mugs.query.all()
    return render_template('inventory.html', mugs=mugs)


@app.route("/panel/addmugs", methods=["POST", "GET"])
def addMug():
    if current_user.is_authenticated:
        if current_user.admin == True:

            mugs = Mugs.query.all()
            if request.method == "POST":

                title = request.form.get('title')
                img_url = request.form.get('img_url')
                caption = request.form.get('caption')
                price = request.form.get('price')
                quantity = request.form.get('quantity')

                mug = Mugs(title, img_url, caption, price, quantity)
                mug.saveToDB()

                flash("Successfully Added Mug to Database!", category='success')
                return render_template('addmugs.html', mugs=mugs)

            else:
                return render_template('addmugs.html')


@app.route("/panel/makeadmin", methods=["POST", "GET"])
def MakeAdminPage():
    if request.method == "POST":
        email = request.form.get('username')
        user = User.query.filter_by(email=email).first()
        user.makeAdmin()
        flash('User Turned Admin')

    return render_template('makeadmin1.html')


@app.route('/meanmugsapi', methods=["GET", "POST"])
def meanmugsapi():
    mugs = Mugs.query.all()
    return jsonify([m.to_dict() for m in mugs])


# @app.before_request
# def database_concction():
#     db.create_all()
#     print('db was created !')


@app.route('/signup', methods=['GET', 'POST'])
def SignUp():
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')

            query = User.query.filter_by(email=email).first()
            if query:
                flash('User Exists')
                return redirect(url_for('SignUp'))
                # create new user
            NewUser = User(name=name, email=email, password=password)
            db.session.add(NewUser)
            db.session.commit()
            login_user(NewUser)
            return redirect(url_for('Panel'))
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = SignInForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = request.form.get('email')
            password = request.form.get('password')
            nextQueryParam = request.form.get('next')
            user = User.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    login_user(user)
                    return redirect(nextQueryParam or url_for('Panel'))
                else:
                    flash(' Wrong Password ')
                    return redirect(url_for('login'))
            else:
                flash('user not found')
                return redirect(url_for('login'))

    return render_template('Login.html', form=form)


@app.route('/panel')
@login_required
def Panel():
    return render_template('panel.html')


@app.route('/panel/editprofile')
@login_required
def EditProfile():
    return 'Edit Profile Page'


@app.route('/panel/upload', methods=['GET', 'POST'])
def UploadAvatar():
    if request.method == 'POST':
        pic = request.form.get('password')
        if pic:
            photo = request.files['pic']
            secureFilename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_DIR'], secureFilename))
            img_path = img_dir + secureFilename
            current_user.avatar = img_path
            db.session.commit()
            return redirect(url_for('Panel'))
        else:
            flash('Please choose a photo first', 'danger')
            return render_template('Avatar.html')
    return render_template('Avatar.html')


@app.route('/panel/edit', methods=['GET', 'POST'])
def UpdateProfile():
    form = UpdateForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.email.data != current_user.email:
                query = User.query.filter_by(email=form.email.data).first()
                if query:
                    flash('User Exists', 'danger')
                    return redirect(url_for('UpdateProfile'))

            current_user.name = form.name.data
            current_user.email = form.email.data
            db.session.commit()

            flash('your account has been updated', 'success')
        return redirect(url_for('UpdateProfile'))

    if request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        return render_template('EditProfile.html', form=form)


@app.route('/panel/changepassword', methods=['POST', 'GET'])
def ChangePassword():
    if request.method == 'POST':
        email = current_user.email

        password = request.form.get('password')
        passwordconfirm = request.form.get('passwordconfirm')
        if password == passwordconfirm:
            user = User.query.filter_by(email=email).first()
            user.password = generate_password_hash(password)
            db.session.commit()
            flash('your account has been updated', 'success')
            return redirect(url_for('ChangePassword'))

    return render_template('changepassword.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('mugs'))


@app.errorhandler(404)
def not_found(err):
    return render_template('404.html')
