from datetime import datetime, UTC
from database import db 

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade="all, delete-orphan")
    company_profile = db.relationship('Company', backref='user', uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    education = db.Column(db.String(200), nullable=True)
    skills = db.Column(db.Text, nullable=True)
    resume_path = db.Column(db.String(255), nullable=True)
    experience = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Student {self.name}>"

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    hr_contact = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(100), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Company {self.company_name}>"
    
class JobPosition(db.Model):
    __tablename__ = 'job_positions'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.String(255), nullable=True)
    salary = db.Column(db.Integer, nullable=True)
    deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    company = db.relationship('Company', backref=db.backref('job_positions', lazy=True))
    applications = db.relationship('Application', backref='job_position', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<JobPosition {self.title} at Company ID {self.company_id}>"
    
class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_positions.id'), nullable=False)
    applied_date = db.Column(db.DateTime, default=datetime.now(UTC))
    status = db.Column(db.String(20), default='Applied')
    student = db.relationship('Student', backref=db.backref('applications', lazy=True))

    def __repr__(self):
        return f"<Application Student ID {self.student_id} for Job ID {self.job_id}>"

class Placement(db.Model):
    __tablename__ = 'placements'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('job_positions.id'), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    joining_date = db.Column(db.DateTime, nullable=True)
    student = db.relationship('Student', backref=db.backref('placements', lazy=True))
    company = db.relationship('Company', backref=db.backref('placements', lazy=True))
    position = db.relationship('JobPosition', backref=db.backref('placements', lazy=True))

    def __repr__(self):
        return f"<Placement Student ID {self.student_id} at Company ID {self.company_id}>"
