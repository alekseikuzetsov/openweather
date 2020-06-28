from flask import Flask
from pymongo import MongoClient


app = Flask(__name__)
app.config['SECRET_KEY'] = 'randomhex'

cluster = MongoClient(
    'mongodb+srv://api_project:8ISEGfTotpk0nar7@myproject-e5syu.mongodb.net/<dbname>?retryWrites=true&w=majority')
db = cluster['myproject']
users = db['Users']
items = db['Items']

@app.route('/register', methods=['POST'])
def register():
    return

@app.route('/login', methods=['POST'])
def login():
    return

@app.route('/items/new', methods=['POST'])
def new_item():
    return

@app.route('/items', methods=['GET'])
def get_items():
    return

@app.route('/items/:id', methods=['DELETE'])
def delete_item(id):
    return