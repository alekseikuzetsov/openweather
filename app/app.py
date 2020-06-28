import datetime
import secrets

import jwt
from functools import wraps

from bson import ObjectId
from pymongo import MongoClient
import flask_bcrypt

from flask import Flask, request, jsonify

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
            return jsonify({'message': 'UNAUTHORISED USER'}), 401

        return f(*args, **kwargs)

    return decorated


@app.route('/register', methods=['POST'])
def register():
    auth = request.authorization
    if auth:
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
@token_required
def new_item():
    token = request.args.get('token')
    user = jwt.decode(token, app.config['SECRET_KEY'])['user']
    name = request.args.get('name')
    item_id = items.insert_one({'name': name, 'owner': user}).inserted_id
    item = items.find_one({'_id': item_id})
    attributes = {key: item[key] for key in item if key not in ['_id', 'owner', 'new_owner']}
    return jsonify({'message': 'ITEM CREATED', 'item_id': str(item_id), 'attributes': attributes})


@app.route('/items', methods=['GET'])
@token_required
def get_items():
    token = request.args.get('token')
    user = jwt.decode(token, app.config['SECRET_KEY'])['user']
    item_list = items.find({'owner': user})
    for_user = {}
    for item in item_list:
        for_user[str(item['_id'])] = {key: item[key] for key in item if key not in ['_id', 'owner', 'new_owner']}
    return jsonify(for_user)


@app.route('/items/<id>', methods=['DELETE'])
@token_required
def delete_item(id):
    token = request.args.get('token')
    user = jwt.decode(token, app.config['SECRET_KEY'])['user']

    try:
        obj_id = ObjectId(id)
    except:
        return jsonify({'message': 'INVALID ITEM ID'}), 400
    item = items.find_one({'_id': obj_id, 'owner': user})
    if item:
        items.delete_many({'_id': obj_id})
    else:
        return jsonify({'message': 'ITEM NOT FOUND'}), 404
    return jsonify({'message': 'ITEM DELETED SUCCESSFULLY'})


@app.route('/send', methods=['POST'])
@token_required
def send():
    token = request.args.get('token')
    item_id = request.args.get('item_id')
    new_owner = request.args.get('new_owner')

    user = jwt.decode(token, app.config['SECRET_KEY'])['user']

    try:
        obj_id = ObjectId(item_id)
    except:
        return jsonify({'message': 'INVALID ITEM ID'}), 400

    item = items.find_one({'_id': obj_id, 'owner': user})
    if item:
        link = secrets.token_hex(20)
        items.update_one({'_id': obj_id}, {'$set': {'new_owner': new_owner, 'link': link}})
    else:
        return jsonify({'message': 'ITEM NOT FOUND'}), 404

    return jsonify({'message': 'ITEM TRANSFER REQUEST RECEIVED', 'link': link})


@app.route('/get', methods=['GET'])
@token_required
def get():
    token = request.args.get('token')
    item_id = request.args.get('item_id')
    link = request.args.get('link')
    user = jwt.decode(token, app.config['SECRET_KEY'])['user']

    try:
        obj_id = ObjectId(item_id)
    except:
        return jsonify({'message': 'INVALID ITEM ID'}), 400

    item = items.find_one({'_id': obj_id, 'new_owner': user, 'link': link})
    if item:
        items.update_one({'_id': obj_id}, {'$set': {'owner': user}})
        items.update_one({'_id': obj_id}, {'$unset': {'new_owner': '', 'link': ''}})
    else:
        return jsonify({'message': 'ITEM NOT FOUND'}), 404
    return jsonify({'message': 'ITEM TRANSFERRED SUCCESSFULLY'})


if __name__ == '__main__':
    app.run()
