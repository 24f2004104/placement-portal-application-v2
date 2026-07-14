import json
import redis
from flask import Blueprint, request, jsonify
from database import db
from models import User, Student, Company, JobPosition, Application, Placement
from datetime import datetime, timezone

dashboard_bp = Blueprint('dashboard', __name__)
#Creating a dedicated redis client for api caching (using database index 1 to keep cache separate from Celery) 
redis_client = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)

# ADMIN ENDPOINTS

#1. Admin metrics overview 
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

#2. Get all students and companies 
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

#3. Toggle user active status 
@dashboard_bp.route('/admin/user/<int:user_id>/toggle-status', methods=['POST'])
def toggle_user_status(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found."}), 444
    
    user.is_active = not user.is_active
    db.session.commit()
    status_str = "activated" if user.is_active else "deactivated"
    return jsonify({"message": f"User account has been {status_str}."}), 200

#4. Approve company profile 
@dashboard_bp.route('/admin/company/<int:company_id>/approve', methods=['POST'])
def approve_company(company_id):
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"message": "Company profile not found."}), 444
    
    company.is_approved = True
    db.session.commit()
    return jsonify({"message": f"Company '{company.company_name}' approved successfully!"}), 200

#5. Fetch all placement drives 
@dashboard_bp.route('/admin/drives', methods=['GET'])
def get_all_drives_admin():
    drives = JobPosition.query.all()
    drive_list = [{
        "id": d.id,
        "company_name": d.company.company_name if d.company else "Unknown/Removed Company",
        "title": d.title,
        "salary": d.salary,
        "deadline": d.deadline.strftime("%Y-%m-%d %H:%M"),
        "status": d.status
    } for d in drives]
    return jsonify({"drives": drive_list}), 200

#6. Admin approve/reject/close placement drive 
@dashboard_bp.route('/admin/drive/<int:drive_id>/status', methods=['POST'])
def update_drive_status(drive_id):
    data = request.get_json()
    new_status = data.get('status')
    
    # Allow Pending, Approved, Rejected, and Closed transitions
    if new_status not in ['Approved', 'Rejected', 'Pending', 'Closed']:
        return jsonify({"message": "Invalid status."}), 400
        
    drive = JobPosition.query.get(drive_id)
    if not drive:
        return jsonify({"message": "Placement drive not found."}), 444
        
    drive.status = new_status
    db.session.commit()
    
    # Refresh Cache Policy: Invalidate cache so students see fresh approved drives immediately
    redis_client.delete('approved_drives_cache')
    
    return jsonify({"message": f"Placement drive status updated to {new_status}."}), 200

#7. Removing/Deleting company profile 
@dashboard_bp.route('/admin/company/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"message": "Company not found."}), 444
        
    user_id = company.user_id
    db.session.delete(company)
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Company profile removed successfully."}), 200

#8. Removing/Deleting a placement drive 
@dashboard_bp.route('/admin/drive/<int:drive_id>', methods=['DELETE'])
def delete_drive_admin(drive_id):
    drive = JobPosition.query.get(drive_id)
    if not drive:
        return jsonify({"message": "Placement drive not found."}), 444
        
    db.session.delete(drive)
    db.session.commit()
    return jsonify({"message": "Placement drive removed successfully."}), 200

#9. Admin - view all applications 
@dashboard_bp.route('/admin/applications', methods=['GET'])
def get_all_applications_admin():
    apps = Application.query.all()
    app_list = [{
        "id": app.id,
        "student_name": app.student.name,
        "education": app.student.education,
        "company_name": app.job_position.company.company_name if app.job_position.company else "Unknown",
        "drive_title": app.job_position.title,
        "applied_date": app.applied_date.strftime("%Y-%m-%d"),
        "status": app.status
    } for app in apps]
    return jsonify({"applications": app_list}), 200

#10. Admin remove/delete a student profile [3]
@dashboard_bp.route('/admin/student/<int:student_id>', methods=['DELETE'])
def delete_student_admin(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student not found."}), 444
        
    user_id = student.user_id
    db.session.delete(student)
    
    # Also delete their login credentials
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        
    db.session.commit()
    return jsonify({"message": "Student profile removed successfully."}), 200


# COMPANY ENDPOINTS 

#1. Post a new placement drive
@dashboard_bp.route('/company/drive', methods=['POST'])
def create_placement_drive():
    data = request.get_json()
    company_id = data.get('company_id')
    title = data.get('title')
    description = data.get('description')
    deadline_str = data.get('deadline')
    
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
        status='Pending'
    )
    
    db.session.add(new_drive)
    db.session.commit()
    return jsonify({"message": "Placement drive created successfully! Awaiting Admin approval."}), 201

#2. Get all drives for a company 
@dashboard_bp.route('/company/<int:company_id>/drives', methods=['GET'])
def get_company_drives(company_id):
    drives = JobPosition.query.filter_by(company_id=company_id).all()
    drive_list = [{
        "id": d.id, "title": d.title, "salary": d.salary, "description": d.description,
        "eligibility_criteria": d.eligibility_criteria,
        "deadline": d.deadline.strftime("%Y-%m-%d %H:%M"),
        "status": d.status
    } for d in drives]
    
    return jsonify({"drives": drive_list}), 200

#3. View applications received for a specific drive 
@dashboard_bp.route('/company/drive/<int:drive_id>/applications', methods=['GET'])
def get_drive_applications(drive_id):
    drive = JobPosition.query.get(drive_id)
    if not drive:
        return jsonify({"message": "Placement drive not found."}), 444
        
    apps = Application.query.filter_by(job_id=drive_id).all()
    app_list = [{
        "application_id": app.id,
        "student_id": app.student.id,
        "student_name": app.student.name,
        "education": app.student.education,
        "applied_date": app.applied_date.strftime("%Y-%m-%d"),
        "status": app.status
    } for app in apps]
        
    return jsonify({
        "drive_title": drive.title,
        "applications": app_list
    }), 200

#4. Shortlist, select, or reject applicants
@dashboard_bp.route('/company/application/<int:app_id>/status', methods=['POST'])
def update_application_status(app_id):
    data = request.get_json()
    new_status = data.get('status')
    
    allowed_statuses = ['Applied', 'Shortlisted', 'Interview', 'Offer', 'Rejected', 'Placed', 'Selected']
    if new_status not in allowed_statuses:
        return jsonify({"message": "Invalid application status."}), 400
        
    app = Application.query.get(app_id)
    if not app:
        return jsonify({"message": "Application not found."}), 444
        
    app.status = new_status
    
    if new_status == 'Selected':
        # Create placement record if student selected
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
    else:
        # If changed away from Selected, deletes any existing placement 
        existing_placement = Placement.query.filter_by(
            student_id=app.student_id, 
            position_id=app.job_id
        ).first()
        if existing_placement:
            db.session.delete(existing_placement)
            
    db.session.commit()
    return jsonify({"message": f"Applicant status updated to '{new_status}' successfully!"}), 200

#5. Modifying/Updating a placement drive
@dashboard_bp.route('/company/drive/<int:drive_id>', methods=['PUT'])
def update_drive_company(drive_id):
    data = request.get_json()
    drive = JobPosition.query.get(drive_id)
    if not drive:
        return jsonify({"message": "Placement drive not found."}), 444
        
    drive.title = data.get('title', drive.title)
    drive.description = data.get('description', drive.description)
    drive.salary = data.get('salary', drive.salary)
    drive.eligibility_criteria = data.get('eligibility_criteria', drive.eligibility_criteria)
    
    if 'status' in data:
        drive.status = data.get('status')
        
    if 'deadline' in data:
        try:
            drive.deadline = datetime.strptime(data.get('deadline'), "%Y-%m-%d %H:%M")
        except ValueError:
            return jsonify({"message": "Invalid date format. Use YYYY-MM-DD HH:MM."}), 400
            
    db.session.commit()
    return jsonify({"message": "Placement drive updated successfully."}), 200

#6. Deleting/Removing a placement drive
@dashboard_bp.route('/company/drive/<int:drive_id>', methods=['DELETE'])
def delete_drive_company(drive_id):
    drive = JobPosition.query.get(drive_id)
    if not drive:
        return jsonify({"message": "Placement drive not found."}), 444
        
    db.session.delete(drive)
    db.session.commit()
    return jsonify({"message": "Placement drive deleted successfully."}), 200

#7. Get company hired candidates (placements)
@dashboard_bp.route('/company/<int:company_id>/placements', methods=['GET'])
def get_company_placements(company_id):
    placements = Placement.query.filter_by(company_id=company_id).all()
    plist = [{
        "id": p.id,
        "student_name": p.student.name,
        "job_title": p.position.title,
        "salary": p.salary,
        "joining_date": p.joining_date.strftime("%Y-%m-%d") if p.joining_date else ""
    } for p in placements]
    return jsonify({"placements": plist}), 200

#8. Set/Update candidate joining date
@dashboard_bp.route('/company/placement/<int:placement_id>/joining-date', methods=['POST'])
def update_joining_date(placement_id):
    data = request.get_json()
    joining_date_str = data.get('joining_date')
    
    placement = Placement.query.get(placement_id)
    if not placement:
        return jsonify({"message": "Placement record not found."}), 444
        
    if not joining_date_str:
        placement.joining_date = None
    else:
        try:
            placement.joining_date = datetime.strptime(joining_date_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({"message": "Invalid date format. Use YYYY-MM-DD."}), 400
            
    db.session.commit()
    return jsonify({"message": "Joining date updated successfully."}), 200


# STUDENT ENDPOINTS 

#1. Fetch approved placement drives  (with search/filter and redis caching)
@dashboard_bp.route('/student/drives', methods=['GET'])
def get_approved_drives():
    search_query = request.args.get('q', '').strip()
    
    #Cache policy: only cache generic listings (when there's no search query)
    if not search_query:
        cached_data = redis_client.get('approved_drives_cache')
        if cached_data:
            print("--- RETRIEVING DRIVES FROM REDIS CACHE ---") # Logs to terminal to prove caching works
            return jsonify({"drives": json.loads(cached_data)}), 200
    
    #If cache misses or a search query is provided, query SQLite
    query = JobPosition.query.filter_by(status='Approved')
    
    if search_query:
        query = query.filter(
            (JobPosition.title.ilike(f"%{search_query}%")) |
            (JobPosition.description.ilike(f"%{search_query}%"))
        )
        
    drives = query.all()
    drive_list = [{
        "id": d.id,
        "company_name": d.company.company_name if d.company else "Unknown Company",
        "title": d.title,
        "description": d.description,
        "salary": d.salary,
        "eligibility_criteria": d.eligibility_criteria,
        "deadline": d.deadline.strftime("%Y-%m-%d %H:%M"),
        "status": d.status
    } for d in drives]
    
    #Expiry policy: If it was a generic query, cache the result in Redis for 60 seconds
    if not search_query:
        redis_client.setex('approved_drives_cache', 60, json.dumps(drive_list))
        
    return jsonify({"drives": drive_list}), 200

#2. Apply to a placement drive
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
        
    if drive.status != 'Approved':
        return jsonify({"message": "Cannot apply to an unapproved placement drive."}), 403
        
    current_time_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    if current_time_naive > drive.deadline:
        return jsonify({"message": "The application deadline for this drive has passed."}), 400
        
    if not student.user.is_active:
        return jsonify({"message": "Your student account is currently deactivated."}), 403
        
    existing_app = Application.query.filter_by(student_id=student_id, job_id=drive_id).first()
    if existing_app:
        return jsonify({"message": "You have already applied to this placement drive."}), 400

    new_application = Application(
        student_id=student_id,
        job_id=drive_id,
        status='Applied'
    )
    
    db.session.add(new_application)
    db.session.commit()
    return jsonify({"message": "Application submitted successfully!"}), 201

#3. View student's complete application history
@dashboard_bp.route('/student/<int:student_id>/applications', methods=['GET'])
def get_student_applications(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student profile not found."}), 444
        
    apps = Application.query.filter_by(student_id=student_id).all()
    history = [{
        "application_id": app.id,
        "drive_id": app.job_position.id,
        "drive_title": app.job_position.title,
        "company_name": app.job_position.company.company_name,
        "applied_date": app.applied_date.strftime("%Y-%m-%d"),
        "status": app.status
    } for app in apps]
        
    return jsonify({"applications": history}), 200

#4. View student's placement results
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

#5. Fetching student profile details
@dashboard_bp.route('/student/<int:student_id>/profile', methods=['GET'])
def get_student_profile(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student profile not found."}), 444
        
    return jsonify({
        "name": student.name,
        "education": student.education,
        "skills": student.skills,
        "experience": student.experience
    }), 200

#6. Updating student profile
@dashboard_bp.route('/student/<int:student_id>/profile', methods=['PUT'])
def update_student_profile(student_id):
    data = request.get_json()
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student profile not found."}), 444
        
    student.name = data.get('name', student.name)
    student.education = data.get('education', student.education)
    student.skills = data.get('skills', student.skills)
    student.experience = data.get('experience', student.experience)
    
    db.session.commit()
    return jsonify({"message": "Profile updated successfully."}), 200

#CELERY TASK ENDPOINTS 

#1. Trigger async csv export
@dashboard_bp.route('/student/<int:student_id>/export-csv', methods=['POST'])
def trigger_csv_export(student_id):
    from app import export_applications_csv
    task = export_applications_csv.delay(student_id)
    return jsonify({
        "message": "Export task started in background...",
        "task_id": task.id
    }), 202

#2.Poll task status 
@dashboard_bp.route('/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    from app import celery
    task = celery.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {"state": task.state, "status": "Pending..."}
    elif task.state == 'SUCCESS':
        response = {"state": task.state, "result": task.result} # Contains file download url
    elif task.state == 'FAILURE':
        response = {"state": task.state, "status": "Task failed."}
    else:
        response = {"state": task.state, "status": task.state}
        
    return jsonify(response), 200