from flask import Blueprint, request, jsonify
from database import db
from models import User, Student, Company, JobPosition, Application, Placement
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

# ADMIN ENDPOINTS

#1.Admin metrics overview
@dashboard_bp.route('/admin/metrics', methods=['GET'])
def get_admin_metrics():
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = JobPosition.query.count()
    total_applications = Application.query.count()
    
    return jsonify({
        "total_students": total_students,
        "total_companies": total_companies,
        "total_drives": total_drives,
        "total_applications": total_applications
    }), 200

#2.Get all students and companies
@dashboard_bp.route('/admin/users', methods=['GET'])
def get_all_users():
    students = Student.query.all()
    companies = Company.query.all()
    
    student_list = [{
        "id": s.id, "name": s.name, "user_id": s.user_id,
        "education": s.education, "skills": s.skills,
        "is_active": s.user.is_active
    } for s in students]
    
    company_list = [{
        "id": c.id, "company_name": c.company_name, "user_id": c.user_id,
        "location": c.location, "industry": c.industry,
        "is_approved": c.is_approved, "is_active": c.user.is_active
    } for c in companies]
    
    return jsonify({
        "students": student_list,
        "companies": company_list
    }), 200

#3.Toggle user active status
@dashboard_bp.route('/admin/user/<int:user_id>/toggle-status', methods=['POST'])
def toggle_user_status(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found."}), 444
    
    user.is_active = not user.is_active
    db.session.commit()
    status_str = "activated" if user.is_active else "deactivated"
    return jsonify({"message": f"User account has been {status_str}."}), 200

#4.Approve company profile
@dashboard_bp.route('/admin/company/<int:company_id>/approve', methods=['POST'])
def approve_company(company_id):
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"message": "Company profile not found."}), 444
    
    company.is_approved = True
    db.session.commit()
    return jsonify({"message": f"Company '{company.company_name}' approved successfully!"}), 200

#5.Search students and companies
@dashboard_bp.route('/admin/search', methods=['GET'])
def admin_search():
    query_type = request.args.get('type') 
    search_query = request.args.get('q', '').strip()
    
    if query_type == 'student':
        #Search by student name or skills
        results = Student.query.filter(
            (Student.name.ilike(f"%{search_query}%")) | 
            (Student.skills.ilike(f"%{search_query}%"))
        ).all()
        data = [{"id": s.id, "name": s.name, "skills": s.skills, "education": s.education} for s in results]
        
    elif query_type == 'company':
        #Search by company name or industry
        results = Company.query.filter(
            (Company.company_name.ilike(f"%{search_query}%")) | 
            (Company.industry.ilike(f"%{search_query}%"))
        ).all()
        data = [{"id": c.id, "company_name": c.company_name, "industry": c.industry, "location": c.location} for c in results]
    else:
        return jsonify({"message": "Invalid search type."}), 400
        
    return jsonify({"results": data}), 200

#6.Approve/Reject placement drive
@dashboard_bp.route('/admin/drive/<int:drive_id>/status', methods=['POST'])
def update_drive_status(drive_id):
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['Approved', 'Rejected']:
        return jsonify({"message": "Invalid status."}), 400
        
    drive = JobPosition.query.get(drive_id)
    if not drive:
        return jsonify({"message": "Placement drive not found."}), 444
        
    drive.status = new_status
    db.session.commit()
    return jsonify({"message": f"Placement drive status updated to {new_status}."}), 200

#7.Remove/Delete company profile 
@dashboard_bp.route('/admin/company/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"message": "Company not found."}), 444
        
    user_id = company.user_id
    db.session.delete(company)
    
    #delete the associated User credentials
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        
    db.session.commit()
    return jsonify({"message": "Company profile removed successfully."}), 200


# COMPANY ENDPOINTS

#1.Post a new placement drive 
@dashboard_bp.route('/company/drive', methods=['POST'])
def create_placement_drive():
    data = request.get_json()
    company_id = data.get('company_id')
    title = data.get('title')
    description = data.get('description')
    deadline_str = data.get('deadline') # Format is YYYY-MM-DD HH:MM
    
    if not company_id or not title or not description or not deadline_str:
        return jsonify({"message": "All fields are required."}), 400
        
    company = Company.query.get(company_id)
    if not company or not company.is_approved:
        return jsonify({"message": "Only approved companies can create placement drives."}), 403
        
    try:
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD HH:MM."}), 400

    new_drive = JobPosition(
        company_id=company_id,
        title=title,
        description=description,
        eligibility_criteria=data.get('eligibility_criteria'),
        salary=data.get('salary'),
        deadline=deadline,
        status='Pending' # Requires Admin approval to go live
    )
    
    db.session.add(new_drive)
    db.session.commit()
    return jsonify({"message": "Placement drive created successfully! Awaiting Admin approval."}), 201

#2.Get all drives for a company 
@dashboard_bp.route('/company/<int:company_id>/drives', methods=['GET'])
def get_company_drives(company_id):
    drives = JobPosition.query.filter_by(company_id=company_id).all()
    drive_list = [{
        "id": d.id, "title": d.title, "salary": d.salary,
        "deadline": d.deadline.strftime("%Y-%m-%d %H:%M"),
        "status": d.status
    } for d in drives]
    
    return jsonify({"drives": drive_list}), 200

#3.View applications received for a specific drive
@dashboard_bp.route('/company/drive/<int:drive_id>/applications', methods=['GET'])
def get_drive_applications(drive_id):
    drive = JobPosition.query.get(drive_id)
    if not drive:
        return jsonify({"message": "Placement drive not found."}), 444
        
    apps = Application.query.filter_by(job_id=drive_id).all()
    app_list = []
    
    for app in apps:
        student = app.student
        app_list.append({
            "application_id": app.id,
            "student_id": student.id,
            "student_name": student.name,
            "skills": student.skills,
            "education": student.education,
            "applied_date": app.applied_date.strftime("%Y-%m-%d"),
            "status": app.status # 'Applied', 'Shortlisted', 'Selected', 'Rejected' [4]
        })
        
    return jsonify({
        "drive_title": drive.title,
        "applications": app_list
    }), 200

# 4. Shortlisting, selecting, or rejecting applicants
@dashboard_bp.route('/company/application/<int:app_id>/status', methods=['POST'])
def update_application_status(app_id):
    data = request.get_json()
    new_status = data.get('status')  
    
    allowed_statuses = ['Applied', 'Shortlisted', 'Interview', 'Offer', 'Placed', 'Selected', 'Rejected']
    if new_status not in allowed_statuses:
        return jsonify({"message": "Invalid application status."}), 400
        
    app = Application.query.get(app_id)
    if not app:
        return jsonify({"message": "Application not found."}), 444
        
    app.status = new_status
    
    if new_status == 'Selected':
        # Checking if placement record already exists to prevent duplicates
        existing_placement = Placement.query.filter_by(
            student_id=app.student_id, 
            position_id=app.job_id
        ).first()
        
        if not existing_placement:
            drive = app.job_position
            new_placement = Placement(
                student_id=app.student_id,
                company_id=drive.company_id,
                position_id=app.job_id,
                salary=drive.salary,
                joining_date=None 
            )
            db.session.add(new_placement)
            
    db.session.commit()
    return jsonify({"message": f"Applicant status updated to '{new_status}' successfully!"}), 200

# STUDENT ENDPOINTS

#1.Fetching approved placement drives (with search/filter)
@dashboard_bp.route('/student/drives', methods=['GET'])
def get_approved_drives():
    search_query = request.args.get('q', '').strip()
    
    query = JobPosition.query.filter_by(status='Approved')

    if search_query:
        query = query.filter(
            (JobPosition.title.ilike(f"%{search_query}%")) |
            (JobPosition.description.ilike(f"%{search_query}%"))
        )
        
    drives = query.all()
    drive_list = []
    
    for d in drives:
        drive_list.append({
            "id": d.id,
            "company_name": d.company.company_name,
            "title": d.title,
            "description": d.description,
            "salary": d.salary,
            "eligibility_criteria": d.eligibility_criteria,
            "deadline": d.deadline.strftime("%Y-%m-%d %H:%M"),
            "status": d.status
        })
        
    return jsonify({"drives": drive_list}), 200


#2.Applying to a placement drive (with safeguards)
@dashboard_bp.route('/student/apply', methods=['POST'])
def apply_to_drive():
    data = request.get_json()
    student_id = data.get('student_id')
    drive_id = data.get('drive_id')
    
    if not student_id or not drive_id:
        return jsonify({"message": "Student ID and Drive ID are required."}), 400
        
    student = Student.query.get(student_id)
    drive = JobPosition.query.get(drive_id)
    
    if not student or not drive:
        return jsonify({"message": "Student or Placement Drive not found."}), 444
        
    #Safeguard1: Ensuring the student only applies to 'Approved' drives
    if drive.status != 'Approved':
        return jsonify({"message": "Cannot apply to an unapproved placement drive."}), 403
        
    #Safeguard2: Ensuring the deadline hasn't passed
    current_time = datetime.now(datetime.UTC).replace(tzinfo=None)
    if current_time > drive.deadline:
        return jsonify({"message": "The application deadline for this drive has passed."}), 400
        
    #Safeguard3: Preventing duplicate applications for the same job
    existing_app = Application.query.filter_by(student_id=student_id, job_id=drive_id).first()
    if existing_app:
        return jsonify({"message": "You have already applied to this placement drive."}), 400
    
    #Safeguard4: Ensuring the student is not blacklisted 
    if not student.user.is_active:
        return jsonify({"message": "Your student account is currently deactivated."}), 403

    # Creating the application record 
    new_application = Application(
        student_id=student_id,
        job_id=drive_id,
        status='Applied' 
    )
    
    db.session.add(new_application)
    db.session.commit()
    
    return jsonify({"message": "Application submitted successfully!"}), 201


#3.Viewing student's complete application history
@dashboard_bp.route('/student/<int:student_id>/applications', methods=['GET'])
def get_student_applications(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student profile not found."}), 444
        
    apps = Application.query.filter_by(student_id=student_id).all()
    history = []
    
    for app in apps:
        drive = app.job_position
        history.append({
            "application_id": app.id,
            "drive_id": drive.id,
            "drive_title": drive.title,
            "company_name": drive.company.company_name,
            "applied_date": app.applied_date.strftime("%Y-%m-%d"),
            "status": app.status 
        })
        
    return jsonify({"applications": history}), 200


#4.Viewing student's succesful placement results 
@dashboard_bp.route('/student/<int:student_id>/placements', methods=['GET'])
def get_student_placements(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student profile not found."}), 444
        
    placements = Placement.query.filter_by(student_id=student_id).all()
    placement_list = [{
        "placement_id": p.id,
        "company_name": p.company.company_name,
        "job_title": p.position.title,
        "salary": p.salary,
        "joining_date": p.joining_date.strftime("%Y-%m-%d") if p.joining_date else "To be announced"
    } for p in placements]
    
    return jsonify({"placements": placement_list}), 200