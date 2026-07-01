from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from database import db
from models import User, Student, Company

auth_bp = Blueprint('auth', __name__)

def generate_token(user_id, role):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps({'user_id': user_id, 'role': role})

@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    name = data.get('name')

    if not username or not password or not name:
        return jsonify({"message": "Username, password and name are required."}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists."}), 400
    
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password, role='student')

    new_student = Student(
        user=new_user,
        name=name,
        education=data.get('education'),
        skills=data.get('skill'),
        experience=data.get('experience')
    )

    db.session.add(new_user)
    db.session.add(new_student)
    db.session.commit()

    return jsonify({"message": "Student registered successfully!"}), 201

@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    company_name = data.get('company_name')

    if not username or not password or not company_name:
        return jsonify({"message": "Username, password, and company name are required."}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists."}), 400
    
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password, role='company')

    new_company = Company(
        user=new_user,
        company_name=company_name,
        industry=data.get('industry'),
        location=data.get('location'),
        hr_contact=data.get('hr_contact'),
        website=data.get('website')
    )

    db.session.add(new_user)
    db.session.add(new_company)
    db.session.commit()

    return jsonify({"message": "Company registered successfully! Awaiting Admin approval."}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required."}), 400
    
    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid username or password"}), 401
    
    if not user.is_active:
        return jsonify({"message": "Your accont has been deactivated. Contact admin."}), 403
    
    if user.role == 'company':
        if not user.company_profile.is_approved:
            return jsonify({"message": "Your registration is pending Admin approval."}), 403
    
    token = generate_token(user.id, user.role)

    return jsonify({
        "message": "Login successful!",
        "token": token,
        "role": user.role,
        "username": user.username
    }), 200