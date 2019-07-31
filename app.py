# This is a micro_service that returns a JSOn Data for any given client  that calls the rest api
import os as os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api


# Initialize the app
app = Flask(__name__)
api = Api(app)

# set the base directory for the app and DB
base_directory = os.path.abspath(os.path.dirname(__file__))

# setup the Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(base_directory, 'db.sqlite')

# db settings to track modifications
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# After DB setup, I have to initialize it using the sqlalchemy brought in above.
db = SQLAlchemy(app)

# Initialize Marshmallow and pass in the app
ma = Marshmallow(app)


# NB: When building a real production API, every class module below should be in its own file.
# Product Class / Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self, name, description, price, qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty


# Product schema -  This is where I use Marshmallow.
# It tells the fields I am allowed to show.

class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'price', 'qty')


# Next is to initialize the schema, by setting it to a variable
product_schema = ProductSchema(strict=True)  # This handles fetching only one product. good for updating and deleting.
products_schema = ProductSchema(many=True, strict=True)  # This handles the fetching of more than just one product

# Next is to create the DB:
# Go into the python console and enter the following cmds:
# 1. from app import db
# 2. db.create_all()
# Next, I have to setup my database file.
# TODO -  set up my database file here.

# Whatever resource(s) I'll have, whether its a product, blogpost, todos, images, etc, i have to create a 'class' for it
# This 'class' is called a MODEL -  when associated with the DB


# Create a route for calling the products
@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    new_product = Product(name, description, price, qty)

    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product)


# Get all products from the DB
@app.route('/product', methods=['GET'])
def get_products():
    all_product = Product.query.all()

    results = products_schema.dump(all_product)

    return jsonify(results.data)


# Get a single product from the DB
@app.route('/product/<id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)

    return product_schema.jsonify(product)


# UPDATE a product
@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)

    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    # create a new object
    product.name = name
    product.description = description
    product.price = price
    product.qty = qty

    db.session.commit()

    return product_schema.jsonify(product)


# DELETE a single product from the DB
@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return product_schema.jsonify(product)


class HelloWorld(Resource):
    def get(self):
        return {'Ethel': 'world'}


# api.add_resource(HelloWorld, '/hello')


todos = {}


class TodoSimple(Resource):
    def get(self, todo_id):
        return {todo_id: todos[todo_id]}

    def put(self, todo_id):
        todos[todo_id] = request.form['data']
        return {todo_id: todos[todo_id]}


api.add_resource(TodoSimple, '/<string:todo_id>')


# run the server
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port='3000')





