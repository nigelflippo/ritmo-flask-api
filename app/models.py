import datetime
from app import app, db, bcrypt
import jwt

class Lessons(db.Model):
	__tablename__ = "lessons"

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	lesson_name = db.Column(db.String(128), nullable=False)
	instructor_id = db.Column(db.Integer, nullable=False)
	student_id = db.Column(db.Integer, nullable=True)
	instrument = db.Column(db.String(128), nullable=False)
	date = db.Column(db.String(128), nullable=False)
	skill_level = db.Column(db.String(128), nullable=False)

	def __init__(self, lesson_name, instructor_id, student_id, instrument, date, skill_level):
		self.lesson_name = lesson_name
		self.instructor_id = instructor_id
		self.student_id = student_id
		self.instrument = instrument
		self.date = date 
		self.skill_level = skill_level

	def serialize(self):
		return {
			'id': self.id,
			'lesson_name': self.lesson_name,
			'instructor_id': self.instructor_id,
			'student_id': self.student_id,
			'instrument': self.instrument,
			'date': self.date,
			'skill_level': self.skill_level
		}

class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    skill_level = db.Column(db.String(128), nullable=True)
    instrument = db.Column(db.String(128), nullable=False)
    instructor = db.Column(db.Boolean, nullable=False, default=False)
    bio = db.Column(db.Text, nullable=False, default="New User Profile")

    def __init__(self, first_name, last_name, email, password, skill_level, instrument, instructor, bio):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.skill_level = skill_level
        self.instrument = instrument
        self.instructor = instructor
        self.bio = bio

    def serialize(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'password': self.password,
            'skill_level': self.skill_level,
            'instrument': self.instrument,
            'instructor': self.instructor,
            'bio': self.bio
        }

    def encode_auth_token(self, user_id):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=1800),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']

        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

class BlacklistToken(db.Model):
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False

