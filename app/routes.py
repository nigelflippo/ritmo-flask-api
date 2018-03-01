from flask import request, make_response, jsonify, abort
from app import app, db, bcrypt

@app.route('/')
def index():
	return "Ritmo API"