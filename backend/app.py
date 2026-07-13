import os
import csv
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone
from flask import Flask
from celery import Celery
from database import db
from models import User, Student, Company, JobPosition, Application, Placement

#1. CELERY FACTORY CONTEXT BINDING 
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'your-super-secret-key-change-this-later'
    
    #Configure SQLite 
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'placement_portal.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    #Configuring celery redis broker & backend
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    
    db.init_app(app)
    
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    
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
            print("Database initialized and Admin user pre-created!")

    return app



app = create_app()
celery = make_celery(app) #Exported celery instance for the worker


#CELERY ASYNC TASKS 

#Task 1: User-triggered csv export 
@celery.task(name='tasks.export_applications_csv')
def export_applications_csv(student_id):
    apps = Application.query.filter_by(student_id=student_id).all()
    
    export_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    filename = f"applications_student_{student_id}.csv"
    filepath = os.path.join(export_dir, filename)
    
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Student ID', 'Company Name', 'Drive Title', 'Application Status', 'Applied Date'])
        
        for app in apps:
            writer.writerow([
                app.student_id,
                app.job_position.company.company_name if app.job_position.company else "Unknown Company",
                app.job_position.title,
                app.status,
                app.applied_date.strftime("%Y-%m-%d")
            ])
            
    print(f"--- CELERY TASK COMPLETE: CSV EXPORTED TO {filepath} ---")
    return f"/static/exports/{filename}" # Returns url relative to flask server 


#Task 2: Daily upcoming drive reminders 
@celery.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    current_time = datetime.now(timezone.utc).replace(tzinfo=None)
    #Finding active drives closing in the next 24 hours
    drives = JobPosition.query.filter(
        JobPosition.status == 'Approved',
        JobPosition.deadline > current_time
    ).all()
    
    for d in drives:
        time_left = d.deadline - current_time
        if time_left.total_seconds() <= 86400: # 24 hours
            #Simulating sms, email or google chat webhook lert
            print(f"--- DAILY REMINDER: Drive '{d.title}' by {d.company.company_name} closes in {time_left}! ---")
    return "Reminders checked."


#Task 3: Monthly activity reports 
@celery.task(name='tasks.send_monthly_report')
def send_monthly_report():
    total_drives = JobPosition.query.count()
    total_selections = Application.query.filter_by(status='Selected').count()
    
    #Generating HTML report structure
    html_report = f"""
    <html>
      <body>
        <h2>Monthly Activity Report - Placement Cell</h2>
        <p>Active placement drives conducted: {total_drives}</p>
        <p>Successful candidates selected: {total_selections}</p>
      </body>
    </html>
    """
    print("--- MONTHLY REPORT GENERATED ---")
    print(html_report)
    return "Monthly report completed."

if __name__ == '__main__':
    app.run(debug=True, port=5000)