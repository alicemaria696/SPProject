from flask import render_template, request, redirect, url_for, flash, session
from app import app, db
from app.models import Teacher, User, Student, Class, Subject, Assignment
import csv
from io import TextIOWrapper
from datetime import datetime

"""@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        reg_id = request.form['reg_id']
        password = request.form['password']

        # Query the user from DB
        user = User.query.filter_by(reg_id=reg_id, password=password).first()

        if user:
            if reg_id.startswith('A'):
                return redirect(url_for('admin_dashboard'))  # Matches the function name below
            elif reg_id.startswith('T'):
                return redirect(url_for('home'))  # Teacher dashboard
            elif reg_id.startswith('S'):
                return redirect(url_for('student_dashboard'))  # Student dashboard
            else:
                return "Unknown role prefix."
        else:
            return "Invalid credentials. Please try again."

    return render_template('login.html')"""
    
    
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        reg_id = request.form['reg_id']
        password = request.form['password']

        # 1. Check Admins
        user = User.query.filter_by(reg_id=reg_id, password=password).first()
        if user and user.role == 'A':
            return redirect(url_for('admin_dashboard'))

        # 2. Check Teachers
        #teacher = Teacher.query.filter_by(reg_id=reg_id, password=password).first()
        #if teacher:
        #    return redirect(url_for('home'))  # or teacher_dashboard

        # 2. Check Teachers
        teacher = Teacher.query.filter_by(reg_id=reg_id, password=password).first()
        if teacher:
            session['teacher_id'] = teacher.id  # ✅ ADD THIS
            return redirect(url_for('home'))

            
        
        
        

        # 3. Check Students
        student = Student.query.filter_by(reg_id=reg_id, password=password).first()
        if student:
            return redirect(url_for('student_dashboard'))

        # If none matched
        flash("Invalid credentials. Please try again.")
        return redirect(url_for('login'))

    return render_template('login.html')



# Admin route
@app.route('/admindashboard')
def admin_dashboard():
    return render_template('admindashboard.html')


# Teacher route
#@app.route('/home')
#def home():
#    return render_template('home.html')


@app.route('/home')
def home():
    # Allow all teachers to view all classes for now
    classes = Class.query.all()
    return render_template('home.html', classes=classes)



# Teacher dashboard (optional extra route if you separate dashboards)
@app.route('/dashboard')
def teacher_dashboard():
    return render_template('dashboard.html')


# Student route
@app.route('/studentdashboard')
def student_dashboard():
    return render_template('studentdashboard.html')

@app.route('/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    if request.method == 'POST':
        reg_id = request.form['reg_id']
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        password = request.form['password']

        new_teacher = Teacher(reg_id=reg_id, name=name, email=email, department=department, password=password)
        db.session.add(new_teacher)
        db.session.commit()
        flash('Teacher added successfully!')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_teacher.html')

@app.route('/upload_csv', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        file = request.files['file']
        stream = TextIOWrapper(file.stream, encoding='utf-8')
        csv_input = csv.reader(stream)
        next(csv_input)  # Skip header row

        for row in csv_input:
            reg_id, name, email, department, password = row
            teacher = Teacher(reg_id=reg_id, name=name, email=email, department=department, password=password)
            db.session.add(teacher)

        db.session.commit()
        flash('CSV uploaded and teachers added.')
        return redirect(url_for('admin_dashboard'))

    return render_template('upload_csv.html')

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        reg_id = request.form['reg_id']
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        class_ = request.form['class_']
        password = request.form['password']

        new_student = Student(reg_id=reg_id, name=name, email=email, department=department, class_=class_, password=password)
        db.session.add(new_student)
        db.session.commit()
        flash('Student added successfully!')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_student.html')

@app.route('/upload_student_csv', methods=['GET', 'POST'])
def upload_student_csv():
    if request.method == 'POST':
        file = request.files['file']
        stream = TextIOWrapper(file.stream, encoding='utf-8')
        csv_input = csv.reader(stream)
        next(csv_input)

        for row in csv_input:
            reg_id, name, email, department, class_, password = row
            student = Student(reg_id=reg_id, name=name, email=email, department=department, class_=class_, password=password)
            db.session.add(student)

        db.session.commit()
        flash('CSV uploaded and students added.')
        return redirect(url_for('admin_dashboard'))

    return render_template('upload_student_csv.html')

@app.route('/view_teachers')
def view_teachers():
    teachers = Teacher.query.all()
    return render_template('view_teachers.html', teachers=teachers)

# View Students
@app.route('/view_students')
def view_students():
    students = Student.query.all()
    return render_template('view_students.html', students=students)
@app.route('/assignment_creation')
def assignment_creation():
    return render_template('assignment_creation.html')



@app.route('/add_class', methods=['GET', 'POST'])
def add_class():
    if request.method == 'POST':
        class_id = request.form['class_id']
        new_class = Class(class_id=class_id)
        db.session.add(new_class)
        db.session.commit()
        flash('Class added successfully!')
        return redirect(url_for('view_classes'))

    return render_template('add_class.html')

@app.route('/view_classes')
def view_classes():
    classes = Class.query.all()
    return render_template('view_classes.html', classes=classes)

@app.route('/delete_class/<int:id>', methods=['POST'])
def delete_class(id):
    class_to_delete = Class.query.get_or_404(id)
    db.session.delete(class_to_delete)
    db.session.commit()
    flash('Class deleted successfully.')
    return redirect(url_for('view_classes'))

@app.route('/class/<int:class_id>/add_subject', methods=['GET', 'POST'])
def add_subject(class_id):
    teacher_id = session.get('teacher_id')  # Assume login sets this
    if request.method == 'POST':
        s_name = request.form['s_name']
        new_subject = Subject(s_name=s_name, class_id=class_id, teacher_id=teacher_id)
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for('view_subjects', class_id=class_id))
    return render_template('add_subject.html', class_id=class_id)


@app.route('/class/<int:class_id>/subjects')
def view_subjects(class_id):
    subjects = Subject.query.filter_by(class_id=class_id).all()
    return render_template('class_dashboard.html', class_id=class_id, subjects=subjects)

@app.route('/class/<int:class_id>/students')
def view_students_by_class(class_id):
    # Step 1: Get the class_id (e.g., 1) -> fetch actual class name (e.g., "4 MCA A")
    class_obj = Class.query.get_or_404(class_id)
    class_name = class_obj.class_id

    # Step 2: Get all students in that class
    students = Student.query.filter_by(class_=class_name).all()

    return render_template('students_by_class.html', class_name=class_name, students=students)


@app.route('/subject/<int:sub_id>/assignments', methods=['GET', 'POST'])
def subject_assignments(sub_id):
    subject = Subject.query.get_or_404(sub_id)

    if request.method == 'POST':
        title = request.form['title']
        time = request.form['time']               # deadline
        total_marks = request.form['total_marks']
        type_ = request.form['type']

        new_assignment = Assignment(
            title=title,
            time=time,
            total_marks=int(total_marks),
            type=type_,
            sub_id=sub_id
        )
        db.session.add(new_assignment)
        db.session.commit()
        flash("Assignment added.")
        return redirect(url_for('subject_assignments', sub_id=sub_id))

    assignments = Assignment.query.filter_by(sub_id=sub_id).all()
    return render_template('assignment_dashboard.html', subject=subject, assignments=assignments)