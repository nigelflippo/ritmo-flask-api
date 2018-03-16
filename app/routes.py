from flask import request, make_response, jsonify, abort, render_template
from app import app, db, bcrypt
from app.models import Users, BlacklistToken

@app.route('/')
def index():
    return "Ritmo API"

@app.route('/users/all', methods=['GET'])
def get_users():
	users = Users.query.order_by(Users.id).all()
	return jsonify({'data': [Users.serialize(user) for user in users]})

@app.route('/users/register', methods=['POST'])
def register():
	post_data = request.get_json()
	email = post_data.get('email')
	password = post_data.get('password')

	if email is None or password is None:
		responseObject = {
			'status': 'error',
			'message': 'Invalid input.'
		}
		return jsonify(responseObject), 400
	if Users.query.filter_by(email=email).first() is not None:
		responseObject = {
			'status': 'error',
			'message': 'User already exists.'
		}
		return jsonify(responseObject), 400
	user = Users(
		first_name = post_data.get('first_name'),
		last_name = post_data.get('last_name'),
		email = post_data.get('email'),
		password = post_data.get('password'),
		skill_level = post_data.get('skill_level'),
		instrument = post_data.get('instrument'),
		instructor = post_data.get('instructor')
	)
	db.session.add(user)
	db.session.commit()

	auth_token = user.encode_auth_token(user.id)
	responseObject = {
		'status': 'success',
		'message': 'Successfully registered',
		'auth_token': auth_token.decode(),
		'instructor': user.instructor
	}
	return jsonify(responseObject), 201

@app.route('/auth/login', methods=['POST'])
def user_login():
	email = request.json.get('email')
	password = request.json.get('password')
	user = Users.query.filter_by(email=email).first()
	if user and bcrypt.check_password_hash(user.password, password):
		auth_token = user.encode_auth_token(user.id)
		if auth_token:
			responseObject = {
				'email': user.email,
				'status': 'success',
				'message': 'Successfully logged in.',
				'auth_token': auth_token.decode(),
				'instructor': user.instructor
			}
			return jsonify(responseObject), 200
	else:
		responseObject = {
			'status': 'error',
			'message': 'Invalid login.'
		}
		return jsonify(responseObject), 404

@app.route('/auth/status', methods=['GET'])
def get_auth():
	auth_header = request.headers.get('Authorization')
	auth_token = auth_header.split(' ')[0]

	if auth_token:
		decoded = Users.decode_auth_token(auth_token)
		if isinstance(decoded, str):
			responseObject = {
			'status': 'error',
			'message': decoded
			}
			return jsonify(responseObject), 401
		else:
			user = Users.query.get(decoded)
			responseObject = {
				'status': 'success',
				'data': {
					'user_id': user.id,
					'first_name': user.first_name,
					'last_name': user.last_name,
					'email': user.email,
					'instructor': user.instructor
				}
			}
			return jsonify(responseObject), 200
	else:
		responseObject = {
			'status': 'error',
			'message': 'Invalid token.'
		}
		return jsonify(responseObject), 401
