import os
from flask import Flask
from werkzeug.security import generate_password_hash
from database import db 
from models import User, Student, Company, JobPosition, Application, Placement

def create_app():
    app = Flask(__name__)
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'placement_portal.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        admin_username = 'admin'
        existing_admin = User.query.filter_by(username=admin_username).first()

        if not existing_admin:
            hashed_password = generate_password_hash('adminpassword')

            admin_user = User(
                username=admin_username,
                password_hash=hashed_password,
                role='admin',
                is_active=True 
            )

            db.session.add(admin_user)
            db.session.commit()
            print("Database initialized and Admin user ('admin' / 'adminpassword') pre-created successfully!")
        else:
            print("Database already initialized. Admin user already exist.")
    return app 

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)