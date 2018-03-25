from flask import request, make_response, jsonify, abort, render_template
from app import app, db, bcrypt
from app.models import Users, Lessons, BlacklistToken

@app.route('/')
def index():
    return "Ritmo API"

@app.route('/lessons/new', methods=['POST'])
def post_lesson():
	post_data = request.get_json()
	date = post_data.get('date')

	if Lessons.query.filter_by(date=date).first() is not None:
		responseObject = {
		'status': 'error',
		'message': 'Lesson already exists.'
		}
		return jsonify(responseObject), 400
	lesson = Lessons(
		lesson_name = post_data.get('lesson_name'),
		instructor_id = post_data.get('instructor_id'),
		student_id = post_data.get('student_id'),
		instrument = post_data.get('instrument'),
		date = post_data.get('date'),
		skill_level = post_data.get('skill_level')
	)
	db.session.add(lesson)
	db.session.commit()

	responseObject = {
		'status': 'success',
		'message': 'Lesson posted.',
		'lesson_name': lesson.lesson_name,
		'skill_level': lesson.skill_level
	}
	return jsonify(responseObject), 201

@app.route('/lessons/<int:id>', methods=['PUT'])
def update_lesson(id):
	patch_data = request.get_json()

	lesson = Lessons.query.get(id)
	student_id = patch_data.get('student_id')

	lesson.student_id = student_id

	db.session.commit()
	return jsonify(Lessons.serialize(lesson))


@app.route('/lessons/all', methods=['GET'])
def get_lessons():
	lessons = Lessons.query.order_by(Lessons.id).all()
	return jsonify({'data': [Lessons.serialize(lesson) for lesson in lessons]})

@app.route('/lessons/<int:id>', methods=['DELETE'])
def delete_lesson(id):
	lesson = Lessons.query.get(id)
	if not lesson:
		abort(400)

	db.session.delete(lesson)
	db.session.commit()
	return jsonify(Lessons.serialize(lesson))

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
	user = Users.query.get(id)
	if not user:
		abort(400)

	db.session.delete(user)
	db.session.commit()
	return jsonify(Users.serialize(user))

@app.route('/users/<int:id>', methods=['PUT'])
def patch_user(id):
	patch_data = request.get_json()

	user = Users.query.get(id)
	avatar = patch_data.get('avatar')

	user.avatar = avatar

	db.session.commit()
	return jsonify(Users.serialize(user))

@app.route('/users/all', methods=['GET'])
def get_users():
	users = Users.query.order_by(Users.id).all()
	return jsonify({'data': [Users.serialize(user) for user in users]})

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
	user = Users.query.get(id)
	if not user:
		abort(400)
	return jsonify(Users.serialize(user))

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
		instructor = post_data.get('instructor'),
		bio = post_data.get('bio'),
		avatar = post_data.get('avatar'),
		phone_number = post_data.get('phone_number')
	)
	db.session.add(user)
	db.session.commit()

	auth_token = user.encode_auth_token(user.id)
	responseObject = {
		'status': 'success',
		'message': 'Successfully registered',
		'auth_token': auth_token.decode(),
		'instructor': user.instructor,
		'id': user.id
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
				'instructor': user.instructor,
				'avatar': user.avatar,
				'phone_number': user.phone_number,
				'id': user.id
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
					'instrument': user.instrument,
					'bio': user.bio,
					'instructor': user.instructor,
					'avatar': user.avatar,
					'phone_number': user.phone_number
				}
			}
			return jsonify(responseObject), 200
	else:
		responseObject = {
			'status': 'error',
			'message': 'Invalid token.'
		}
		return jsonify(responseObject), 401
