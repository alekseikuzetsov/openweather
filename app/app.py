import datetime

import flask_bcrypt
import jwt
from flask import Flask, request, jsonify
from pymongo import MongoClient
from functools import wraps


app = Flask(__name__)
app.config['SECRET_KEY'] = 'randomhex'

cluster = MongoClient(
    'mongodb+srv://api_project:8ISEGfTotpk0nar7@myproject-e5syu.mongodb.net/<dbname>?retryWrites=true&w=majority')
db = cluster['myproject']
users = db['Users']
items = db['Items']

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'UNAUTHORISED USER'})

        return f(*args, **kwargs)

    return decorated

@app.route('/register', methods=['POST'])
def register():
    auth = request.authorization
    if not auth is None:
        if auth.username == '':
            return jsonify({'message': 'USERNAME MUST BE NON-EMPTY'})
        if auth.password == '':
            return jsonify({'message': 'PASSWORD MUST BE NON-EMPTY'})

        if users.find_one({'username': auth.username}):
            return jsonify({'message': 'USERNAME IS IN USE'})
        else:
            hashed_password = flask_bcrypt.generate_password_hash(auth.password).decode('utf-8')
            users.insert_one({'username': auth.username, 'password': hashed_password})
            return jsonify({'message': 'REGISTERED SUCCESSFULLY'})
    return jsonify({'message': 'CREDENTIAL DETAILS REQUIRED'})


@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if auth and auth.username and auth.password:
        user = users.find_one({'username': auth.username})
        if user and flask_bcrypt.check_password_hash(user['password'], auth.password):
            token = jwt.encode({'user': auth.username,
                               'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
                                },
                               app.config['SECRET_KEY'])
            return jsonify({'token': token.decode('UTF-8')})
        else:
            return jsonify({'message': 'INVALID LOGIN OR PASSWORD'})
    return jsonify({'message': 'CREDENTIAL DETAILS REQUIRED'})

@app.route('/items/new', methods=['POST'])
def new_item():
    return

@app.route('/items', methods=['GET'])
def get_items():
    return

@app.route('/items/:id', methods=['DELETE'])
def delete_item(id):
    return

if __name__ == '__main__':
    app.run()
