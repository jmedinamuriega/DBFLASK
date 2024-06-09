from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from datetime import date
from password import password

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (f"mysql+mysqlconnector://root:{password}@localhost/dbflask")
db = SQLAlchemy(app)
ma = Marshmallow(app)

#Here are the necessary tables for the database7
class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(155))
    phone = db.Column(db.String(15))
    orders = db.relationship("Order", backref='customer')
    customer_account = db.relationship("CustomerAccount", backref="customer", uselist=False)

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))

order_product = db.Table(
    "order_product",
    db.Column("order_id", db.Integer, db.ForeignKey("orders.id"), primary_key=True),
    db.Column("product_id", db.Integer, db.ForeignKey("products.id"), primary_key=True)
)

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    orders = db.relationship("Order", secondary=order_product, backref=db.backref("products"))

class CustomerAccount(db.Model):
    __tablename__ = "customer_accounts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))


#Here is where I made all the schemas
class CustomerSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "email", "phone")

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

class ProductSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "price", "stock")

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

class OrderSchema(ma.Schema):
    class Meta:
        fields = ("id", "date", "customer_id", "products")

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

class CustomerAccountSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "customer_id")

customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)

#Here are the CRUD operators

@app.route("/customers", methods=["POST"])
def create_customer():
    try:
        data = request.json
        name = data["name"]
        email = data["email"]
        phone = data["phone"]
        new_customer = Customer(name=name, email=email, phone=phone)
        db.session.add(new_customer)
        db.session.commit()
        return customer_schema.jsonify(new_customer), 201
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

@app.route("/customers/<int:id>", methods=["GET"])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return customer_schema.jsonify(customer)

@app.route("/customers/<int:id>", methods=["PUT"])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    data = request.json
    customer.name = data.get("name", customer.name)
    customer.email = data.get("email", customer.email)
    customer.phone = data.get("phone", customer.phone)
    db.session.commit()
    return customer_schema.jsonify(customer)

@app.route("/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "customer removed"}), 200


@app.route("/customer_accounts", methods=["POST"])
def create_customer_account():
    try:
        data = request.json
        username = data["username"]
        customer_id = data["customer_id"]
        new_account = CustomerAccount(username=username, customer_id=customer_id)
        db.session.add(new_account)
        db.session.commit()
        return customer_account_schema.jsonify(new_account), 201
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

@app.route("/customer_accounts/<int:id>", methods=["GET"])
def get_customer_account(id):
    account = CustomerAccount.query.get_or_404(id)
    return customer_account_schema.jsonify(account)

@app.route("/customer_accounts/<int:id>", methods=["PUT"])
def update_customer_account(id):
    account = CustomerAccount.query.get_or_404(id)
    data = request.json
    account.username = data.get("username", account.username)
    db.session.commit()
    return customer_account_schema.jsonify(account)

@app.route("/customer_accounts/<int:id>", methods=["DELETE"])
def delete_customer_account(id):
    account = CustomerAccount.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({"message": "customer account removed"}), 200


@app.route("/products", methods=["POST"])
def create_product():
    try:
        data = request.json
        name = data["name"]
        price = data["price"]
        stock = data["stock"]
        new_product = Product(name=name, price=price, stock=stock)
        db.session.add(new_product)
        db.session.commit()
        return product_schema.jsonify(new_product), 201
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

@app.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    product = Product.query.get_or_404(id)
    return product_schema.jsonify(product)

@app.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.json
    product.name = data.get("name", product.name)
    product.price = data.get("price", product.price)
    product.stock = data.get("stock", product.stock)
    db.session.commit()
    return product_schema.jsonify(product)

@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "product removed"}), 200

@app.route("/products", methods=["GET"])
def list_products():
    products = Product.query.all()
    return products_schema.jsonify(products)


@app.route("/orders", methods=["POST"])
def place_order():
    try:
        data = request.json
        customer_id = data["customer_id"]
        product_ids = data["product_ids"]
        new_order = Order(customer_id=customer_id)
        db.session.add(new_order)
        for product_id in product_ids:
            product = Product.query.get_or_404(product_id)
            new_order.products.append(product)
        db.session.commit()
        return order_schema.jsonify(new_order), 201
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

@app.route("/orders/<int:id>", methods=["GET"])
def retrieve_order(id):
    order = Order.query.get_or_404(id)
    return order_schema.jsonify(order)

#delete order
@app.route("/orders/<int:id>", methods=["DELETE"])
def cancel_order(id):
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "order canceled"}), 200

#Create the necesary tables for the database
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
