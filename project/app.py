import os

from sqlalchemy import exc
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from flask import Flask, redirect, render_template, request, session, flash, url_for
from flask_session import Session 
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

#Configure application
app = Flask(__name__)

# Format the price 2 digits after decimal
def usd(price):
    return f"${price:,.2f}"
# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Configure SQLAlchemy to interact with the database
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///C:\Users\Admin\OneDrive\project\albums.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Ensure all database actions happen within an app context
with app.app_context():
    Base = automap_base()
    Base.prepare(db.engine, reflect=True)

    Users = Base.classes.users
    Albums = Base.classes.albums
    Orders = Base.classes.orders
    Items = Base.classes.order_items
    db_session = db.session()
#Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def after_request(response):
    """Ensure response aren't cached"""
    response.headers['Cache-Control'] = "no-cache, no-store, must-revalidate"
    response.headers['Expires'] = 0
    response.headers['Pragma'] = 'no-cache'
    return response

# Hanlde error 404 page
@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html"),404

@app.route("/")
def index():
    albums = db_session.query(Albums).limit(10).all()
    return render_template("index.html",albums=albums)

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check valid input
        if not username:
            flash("Must enter username","danger")
            return redirect("/login")
        if not password:
            flash("Must enter password","danger")
            return redirect("/login")
        users = db_session.query(Users).filter_by(username = username).first()
        if users is None or not check_password_hash(users.password,password):
            flash("Invalid username and/or password","danger")
            return redirect("/login")
        #Remember who is logging in
        session["user_id"] = users.id

        flash("Login successfully !","success")
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!","success")
    return redirect("/")

@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone = request.form.get("phone")
        address = request.form.get("address")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        
        if password == confirmation:
            hashed_password = generate_password_hash(password)
            new_users = Users(username=username, password=hashed_password, first_name = first_name\
                              ,last_name = last_name, phone = phone, address = address)
            try:
                db_session.add(new_users)
                db_session.commit()
                flash("Registration successful! Please log in","success")
                return render_template("login.html")
            except exc.SQLAlchemyError:
                db_session.rollback()
                flash("Username is already taken","danger")
                return redirect("/register")
        else:
            flash("Fail to confirm password","danger")
            return redirect("/register")
    else:
        return render_template("register.html")

@app.route("/change", methods=["POST","GET"])
def change():
    if request.method == "POST":
        user_id = session["user_id"]
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")
        user = db_session.query(Users).filter_by(id=user_id).first()
        current_password = user.password

        # Check valid input
        if old_password == new_password:
            flash("Same new password !","dangger")
            return redirect("/change")
        if not check_password_hash(current_password,old_password):
            flash("Your current password is invalid","danger")
            return redirect("/change")
        if new_password == confirmation:
            hashed_new_password = generate_password_hash(new_password)
            user.password = hashed_new_password
            db_session.commit()
            flash("Change password successfully !","success")
            return redirect("/login")
        else:
            flash("Failt to confirm new password","danger")
            return redirect("/change")
    else:
        return render_template("change.html")
    
@app.route("/shop", methods=["POST","GET"])
def shop():
    page_number = request.args.get('page',1,type=int)
    albums_per_page = 12
    offset_value = (page_number - 1) * albums_per_page

    albums = db_session.query(Albums).offset(offset_value).limit(12).all()

    total_albums = db_session.query(Albums).count()
    total_pages = (total_albums + 9) // 12
    if request.method == "POST":
        return render_template("shop.html", albums=albums, page_number=page_number, total_pages=total_pages)
    else:
        return render_template("shop.html", albums=albums, page_number=page_number, total_pages=total_pages, total_albums=total_albums)

@app.route("/add_to_cart/",methods=["POST"])
@login_required
def add_to_cart():
    user_id = session["user_id"]
    album_id = request.form.get("album_id", type=int)

    album = db_session.query(Albums).get(album_id)
    if not album:
        flash("Album not found ! ", "danger")
        return redirect("/shop")

    # Check for existing pending order
    order = db_session.query(Orders).filter_by(user_id = user_id, status = "Pending").first()

    # If no pending order, create one
    if not order:
        order = Orders(user_id = user_id, total_price = 0, status = "Pending")
        db_session.add(order)
        db_session.commit()
    
    # Check if item is already in the cart
    cart_item = db_session.query(Items).filter(Items.order_id == order.id, Items.album_id == album.id).first()
    if not cart_item:
        cart_item = Items(order_id = order.id, album_id = album_id, quantity = 1)
        db_session.add(cart_item)
        db_session.commit()
    else:
        cart_item.quantity += 1
        db_session.commit()

    #Update total price of the order
    order.total_price += album.price
    db_session.commit()

    flash(f"{album.title} has been added to your cart","success")
    return redirect("/shop")        

@app.route("/remove_item", methods=["POST"])
def remove_item():
    item_id = request.form.get("item_id", type=int)

    # Fetch the item and album price, but first check if the result is None
    result = db_session.query(Items, Albums.price).join(Albums, Items.album_id == Albums.id).filter(Items.id == item_id).first()

    if not result:
        flash("Item not found", "danger")
        return redirect("/cart")

    item, album_price = result  # Unpack after checking it's not None

    # Process the order as before
    order = db_session.query(Orders).filter_by(id=item.order_id).first()
    if order:
        order.total_price -= album_price * item.quantity
        db_session.delete(item)
        db_session.commit()
        flash(f"Removed successfully!", "success")
    else:
        flash("Order not found", "danger")

    return redirect("/cart")

@app.route("/cart", methods = ["GET"])
@login_required
def cart():
    user_id = session["user_id"]
    order = db_session.query(Orders).filter_by(user_id = user_id, status = "Pending").first()

    if not order:
            flash("You have not bought anything yet","info")
            return render_template("cart.html")
    
    cart_items = db_session.query(Items.quantity, Items.id, Albums.title, Albums.cover, Albums.price, Albums.artist)\
            .join(Albums, Items.album_id == Albums.id)\
            .filter(Items.order_id == order.id).all()

    total_price = order.total_price

    if request.method == "GET":
        return render_template("cart.html", cart_items = cart_items, total_price = total_price)


@app.route("/update_quantity", methods=["POST"])
def update_quantity():
    item_id = request.form.get("item_id", type=int)

    item = db_session.query(Items).filter_by(id=item_id).first()
    order = db_session.query(Orders).filter_by(id=item.order_id).first()
    item_price = db_session.query(Albums).filter_by(id=item.album_id).first().price

    if 'add' in request.form:
        item.quantity += 1
        order.total_price += item_price
        db_session.commit()
    elif 'minus' in request.form and item.quantity > 1:
        item.quantity -= 1
        order.total_price -= item_price
        db_session.commit()
    
    return redirect("/cart")    

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    phone = request.form.get("phone")
    address = request.form.get("address")

    user_id = session["user_id"]
    order = db_session.query(Orders).filter_by(user_id = user_id, status="Pending").first()
    user = db_session.query(Users).filter_by(id  = user_id).first()
    cart_items = db_session.query(Items.quantity,Items.order_id, Albums.price, Albums.artist, Albums.title)\
                .join(Albums, Items.album_id == Albums.id)\
                .join(Orders, Items.order_id == Orders.id).all()
    
    if not order:
        return redirect("/cart")
    
    total_price = order.total_price


    if request.method == "POST":
        if user.cash >= order.total_price:
            #Update user cash
            updated_cash = user.cash - order.total_price
            user.cash = updated_cash
            db_session.commit()
            #Update order information if the user make changes
            order.first_name = first_name
            order.last_name = last_name
            order.phone = phone
            order.address = address
            order.status = "Purchased"
            db_session.commit()
            flash("Purchase successfully !", "success")
            return redirect("/")
        else:
            flash("You do not have enough cash","danger")
            return redirect("/checkout")
    else:
        return render_template("checkout.html",cart_items = cart_items, total_price = total_price, user = user, order = order) 

@app.route("/history", methods=["GET"])
@login_required
def history():
    user_id = session["user_id"]
    orders = db_session.query(Orders).filter_by(user_id = user_id).all()
    if not orders:
        flash("You have not purchased any orders yet !", "info")
        return render_template("history.html")

    items = db_session.query(Items.quantity, Items.order_id, Albums.cover, Albums.title, Albums.genre\
                              ,Albums.artist, Albums.label, Orders.total_price, Orders.status, Orders.order_date,)\
                        .join(Orders, Items.order_id == Orders.id)\
                        .join(Albums, Items.album_id == Albums.id).all()
    
    return render_template("history.html",orders = orders, items = items)

@app.route("/account", methods=["POST","GET"])
@login_required
def account():
    user_id = session["user_id"]
    user = db_session.query(Users).filter_by(id=user_id).first()

    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone = request.form.get("phone")
        address = request.form.get("address")
        
        db_session.query(Users).filter_by(id = user_id).update({
           Users.first_name : first_name,
           Users.last_name : last_name,
            Users.phone : phone,
            Users.address : address
        })

        db_session.commit()
        flash("Update successfully","success")
        return redirect("/account")
    else:
        return render_template("account.html", user=user)

if __name__ == '__main__':
    app.run(debug=True)