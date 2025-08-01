from flask import json, render_template, request, redirect, url_for, flash, session
from app import app, db
from app.models import Teacher, User, Student, Class, Subject, Assignment, Submission, Result, ScriptAssignment
from datetime import datetime
import csv
from io import TextIOWrapper
import os
from werkzeug.utils import secure_filename
from flask import jsonify
from PyPDF2 import PdfReader
import re
import docx2txt 

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        reg_id = request.form['reg_id']
        password = request.form['password']

        user = User.query.filter_by(reg_id=reg_id, password=password).first()
        if user and user.role == 'A':
            return redirect(url_for('admin_dashboard'))

        teacher = Teacher.query.filter_by(reg_id=reg_id, password=password).first()
        if teacher:
            session['teacher_id'] = teacher.id
            return redirect(url_for('home'))

        student = Student.query.filter_by(reg_id=reg_id, password=password).first()
        if student:
            session['reg_id'] = student.reg_id
            return redirect(url_for('student_dashboard'))

        flash("Invalid credentials. Please try again.")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/admindashboard')
def admin_dashboard():
    return render_template('admindashboard.html')

@app.route('/home')
def home():
    classes = Class.query.all()
    return render_template('home.html', classes=classes)

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
        next(csv_input)

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

@app.route('/view_students')
def view_students():
    students = Student.query.all()
    return render_template('view_students.html', students=students)

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
    teacher_id = session.get('teacher_id')
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
    class_obj = Class.query.get_or_404(class_id)
    class_name = class_obj.class_id
    students = Student.query.filter_by(class_=class_name).all()
    return render_template('students_by_class.html', class_name=class_name, students=students)

@app.route('/subject/<int:sub_id>/assignments', methods=['GET', 'POST'])
def subject_assignments(sub_id):
    subject = Subject.query.get_or_404(sub_id)
    if request.method == 'POST':
        title = request.form['title']
        time = request.form['time']
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
    return render_template("assignment_dashboard.html", subject=subject, assignments=assignments)

@app.route('/subject/<int:sub_id>/assignments/create', methods=['GET', 'POST'])
def create_assignment(sub_id):
    subject = Subject.query.get_or_404(sub_id)
    if request.method == 'POST':
        title = request.form['title']
        type_ = request.form['type']
        time = request.form['time']
        total_marks = request.form['total_marks']
        questions = request.form.get('questions')
        rubric = request.form.get('rubric')
        keywords = request.form.get('keywords')

        new_assignment = Assignment(
            title=title,
            type=type_,
            time=time,
            total_marks=total_marks,
            sub_id=sub_id,
            questions=questions,
            rubric=rubric,
            keywords=keywords
        )
        db.session.add(new_assignment)
        db.session.commit()
        flash('Assignment created successfully!')
        return redirect(url_for('subject_assignments', sub_id=sub_id))

    return render_template('assignment_creation.html', subject=subject)

"""@app.route('/studentdashboard')
def student_dashboard():
    student_reg_id = session.get('reg_id')
    student = Student.query.filter_by(reg_id=student_reg_id).first()
    class_id = Class.query.filter_by(class_id=student.class_).first().id
    subjects = Subject.query.filter_by(class_id=class_id).all()

    all_assignments = []
    for subject in subjects:
        assignments = Assignment.query.filter_by(sub_id=subject.sub_id).all()
        for a in assignments:
            all_assignments.append({
                'title': a.title,
                'date': a.timestamp.strftime('%Y-%m-%d'),
                'subject': subject.s_name
            })

    return render_template('studentdashboard.html', assignments=all_assignments)"""

@app.route('/studentdashboard')
def student_dashboard():
    student_reg_id = session.get('reg_id')
    student = Student.query.filter_by(reg_id=student_reg_id).first()
    class_id = Class.query.filter_by(class_id=student.class_).first().id
    subjects = Subject.query.filter_by(class_id=class_id).all()

    all_assignments = []
    for subject in subjects:
        assignments = Assignment.query.filter_by(sub_id=subject.sub_id).all()
        for a in assignments:
            formatted_time = a.time.strftime('%Y-%m-%d %H:%M') if isinstance(a.time, datetime) else a.time.replace('T', ' ')
            all_assignments.append({
                'assignment_id': a.id,
                'title': a.title,
                'timestamp': a.timestamp.strftime('%Y-%m-%d %H:%M'),
                'time': formatted_time,
                'type': a.type,
                'total_marks': a.total_marks,
                'subject': subject.s_name,
                'questions': a.questions  # ✅ Include questions here
            })
                    # ✅ Script-based assignments
        script_assignments = ScriptAssignment.query.filter_by(sub_id=subject.sub_id).all()
        for sa in script_assignments:
            deadline_formatted = (
        sa.deadline.strftime('%Y-%m-%d %H:%M')
        if isinstance(sa.deadline, datetime)
        else str(sa.deadline).replace('T', ' ')
    )
    all_assignments.append({
        'assignment_id': sa.id,
        'title': sa.title,
        'timestamp': 'N/A',
        'time': deadline_formatted,
        'type': 'script',
        'total_marks': sa.total_marks,
        'subject': subject.s_name,
        'questions': sa.questions
    })


    return render_template('studentdashboard.html', assignments=all_assignments)



@app.route('/upload_submission/<int:assignment_id>', methods=['POST'])
def upload_submission(assignment_id):
    student_id = session.get('reg_id')
    assignment = Assignment.query.get_or_404(assignment_id)
    subject = Subject.query.get(assignment.sub_id)

    if 'document' not in request.files:
        flash('No file uploaded.')
        return redirect(url_for('studentdashboard'))

    file = request.files['document']
    if file.filename == '':
        flash('No selected file.')
        return redirect(url_for('studentdashboard'))

    filename = secure_filename(file.filename)
    filepath = os.path.join('uploads', filename)
    file.save(filepath)

    new_submission = Submission(
        student_id=student_id,
        subject_name=subject.s_name,
        submitted_document=filename
    )
    db.session.add(new_submission)
    db.session.commit()

    flash('Assignment uploaded successfully!')
    return redirect(url_for('studentdashboard'))


"""@app.route('/evaluate_submission', methods=['POST'])
def evaluate_submission():
    assignment_title = request.form['assignment_title']
    file = request.files['document']

    # Save file
    filepath = os.path.join('uploads', file.filename)
    file.save(filepath)
    

    # Fetch assignment info
    assignment = Assignment.query.filter_by(title=assignment_title).first()
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404

    # Extract keywords
    keywords = [k.strip().lower() for k in assignment.keywords.split(',')] if assignment.keywords else []

    # Extract text from file
    if file.filename.endswith('.pdf'):
        reader = PdfReader(filepath)
        text = ''.join([page.extract_text() for page in reader.pages])
    elif file.filename.endswith('.docx'):
        text = docx2txt.process(filepath)
    else:
        text = file.read().decode('utf-8')

    # Keyword matching
    words = re.findall(r'\w+', text.lower())
    match_count = sum(1 for kw in keywords if kw in words)

    # Evaluate
    marks = 70 if match_count >= 3 else 0
    status = 'Pass' if marks > 0 else 'Fail'
    on_time = datetime.now() <= datetime.strptime(assignment.time, "%Y-%m-%dT%H:%M")

    # Save submission to DB
    student_id = session.get('reg_id')
    submission = Submission(
        student_id=student_id,
        subject_name=assignment.subject.s_name,
        file_name=file.filename,
        uploaded_at=datetime.now(),
        marks=marks,
        status=status,
        on_time=on_time
    )
    db.session.add(submission)
    db.session.commit()

    return jsonify({
        'title': assignment.title,
        'matches': match_count,
        'marks': marks,
        'status': status,
        'on_time': on_time
    })"""
    
    
"""@app.route('/evaluate_submission', methods=['POST'])
def evaluate_submission():
    assignment_title = request.form['assignment_title']
    file = request.files['document']

    # Create uploads folder if not exists
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    # Secure and save file
    filename = secure_filename(file.filename)
    filepath = os.path.join(uploads_dir, filename)
    file.save(filepath)

    # Fetch assignment info
    assignment = Assignment.query.filter_by(title=assignment_title).first()
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404

    # ✅ Fetch the subject name using assignment.sub_id
    subject = Subject.query.get(assignment.sub_id)
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404

    # Extract keywords
    keywords = [k.strip().lower() for k in assignment.keywords.split(',')] if assignment.keywords else []

    # Extract text from file
    try:
        if filename.endswith('.pdf'):
            reader = PdfReader(filepath)
            text = ''.join([page.extract_text() or '' for page in reader.pages])
        elif filename.endswith('.docx'):
            text = docx2txt.process(filepath)
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
    except Exception as e:
        return jsonify({'error': f"Error reading file: {str(e)}"}), 500

    # Keyword matching
    words = re.findall(r'\w+', text.lower())
    match_count = sum(1 for kw in keywords if kw in words)

    # Time evaluation
    try:
        deadline = datetime.strptime(assignment.time, "%Y-%m-%dT%H:%M")
    except ValueError:
        return jsonify({'error': 'Invalid deadline format'}), 400

    on_time = datetime.now() <= deadline

    # Evaluation
    marks = 70 if match_count >= 3 else 0
    status = 'Pass' if marks > 0 else 'Fail'

    # Save submission to DB
    student_id = session.get('reg_id')
    submission = Submission(
    assignment_id=assignment.id,
    student_id=student_id,
    subject_name=subject.s_name,
    submitted_document=filename,  # ✅ Correct field name
    upload_time=datetime.now(),
    marks=marks,
    status=status,
    on_time=on_time
)
    db.session.add(submission)
    db.session.commit()

    return jsonify({
        'title': assignment.title,
        'matches': match_count,
        'marks': marks,
        'status': status,
        'on_time': on_time
    })"""
    
@app.route('/evaluate_submission', methods=['POST'])
def evaluate_submission():
    import spacy
    from collections import Counter
    from flask import request, jsonify, session
    from werkzeug.utils import secure_filename
    from datetime import datetime
    from PyPDF2 import PdfReader
    import docx2txt
    import os
    import requests
    import base64
    import time

    try:
        nlp = spacy.load("en_core_web_md")
    except:
        nlp = spacy.load("en_core_web_sm")
        print("⚠️ Warning: Falling back to en_core_web_sm — semantic scoring may be weaker.")

    assignment_title = request.form['assignment_title']
    file = request.files['document']

    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

    filename = secure_filename(file.filename)
    filepath = os.path.join(uploads_dir, filename)
    file.save(filepath)

    assignment = Assignment.query.filter_by(title=assignment_title).first()
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404

    keywords = [k.strip().lower() for k in assignment.keywords.split(',')] if assignment.keywords else []

    try:
        if filename.endswith('.pdf'):
            reader = PdfReader(filepath)
            text = ''.join([page.extract_text() or '' for page in reader.pages])
        elif filename.endswith('.docx'):
            text = docx2txt.process(filepath)
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
    except Exception as e:
        return jsonify({'error': f"Error reading file: {str(e)}"}), 500

    doc = nlp(text.lower())
    words = [token.text for token in doc if token.is_alpha]
    word_freq = Counter(words)

    match_count = sum(word_freq.get(kw, 0) for kw in keywords)
    keyword_score = min(match_count / max(len(keywords), 1), 1.0) * 100

    word_count = len(words)
    word_score = 100 if word_count >= 100 else word_count

    try:
        deadline = datetime.strptime(assignment.time, "%Y-%m-%dT%H:%M")
    except ValueError:
        return jsonify({'error': 'Invalid deadline format'}), 400

    on_time = datetime.now() <= deadline
    deadline_score = 100 if on_time else 0

    semantic_score = 0
    for kw in keywords:
        kw_doc = nlp(kw)
        similarities = [kw_doc.similarity(sent) for sent in doc.sents]
        if similarities and max(similarities) > 0.75:
            semantic_score += 1
    semantic_score = (semantic_score / len(keywords)) * 100 if keywords else 0

    # Updated plagiarism check with Winston AI
    plagiarism_score = 0
    try:
        WINSTON_API_KEY = "a5q1MDQhH20YFDMAfKRKTmutOhrxtIJ7SmTzurjbb40aee90"
        headers = {
            "Authorization": f"Bearer {WINSTON_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "content": text,
            "filename": filename
        }
        response = requests.post("https://api.winston.ai/plagiarism-check", json=data, headers=headers)
        if response.status_code == 200:
            resp_json = response.json()
            plagiarism_score = resp_json.get("plagiarism_percentage", 0)
        else:
            raise Exception(f"Winston API failed: {response.text}")
    except Exception as e:
        print("Plagiarism check failed:", e)

    plagiarism_penalty = 0 if plagiarism_score <= 20 else 0

    total_score = (keyword_score + word_score + deadline_score + semantic_score + plagiarism_penalty) / 5
    status = 'Pass' if total_score >= 50 else 'Fail'

    student_id = session.get('reg_id')
    subject = Subject.query.filter_by(sub_id=assignment.sub_id).first()

    submission = Submission(
        assignment_id=assignment.id,
        student_id=student_id,
        subject_name=subject.s_name,
        submitted_document=filename,
        upload_time=datetime.now(),
        marks=int(total_score),
        status=status,
        on_time=on_time
    )
    db.session.add(submission)

    result = Result(
        assignment_id=assignment.id,
        student_id=student_id,
        subject_name=subject.s_name,
        file_name=filename,
        total_matches=match_count,
        marks=int(total_score),
        status=status,
        on_time=on_time,
        evaluated_at=datetime.now()
    )
    db.session.add(result)
    db.session.commit()

    return jsonify({
        'title': assignment.title,
        'matches': match_count,
        'marks': int(total_score),
        'status': status,
        'on_time': on_time,
        'plagiarism': f"{plagiarism_score:.2f}%"
    })


    
@app.route('/teacher/<int:class_id>/performance')
def student_performance(class_id):
    results = Result.query.join(Assignment, Result.assignment_id == Assignment.id)\
                          .join(Subject, Assignment.sub_id == Subject.sub_id)\
                          .filter(Subject.class_id == class_id)\
                          .order_by(Result.evaluated_at.desc()).all()
    subjects = Subject.query.filter_by(class_id=class_id).all()
    return render_template('class_dashboard.html', results=results, subjects=subjects, class_id=class_id)

def evaluate_script(compilation_success, deadline_time):
    on_time = datetime.now() <= deadline_time
    if compilation_success and on_time:
        return 100, "✅ Compilation Successful - Submitted on Time", True
    elif compilation_success:
        return 70, "✅ Compilation Successful - ❌ Deadline Missed", False
    else:
        return 0, "❌ Compilation Failed", False


@app.route('/evaluate_script', methods=['POST'])
def evaluate_script_route():
    from flask import request, jsonify
    data = request.get_json()
    assignment_id = data.get("assignment_id")
    compilation_success = data.get("compilation_success")

    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({'message': 'Assignment not found', 'marks': 0}), 404

    try:
        deadline_time = datetime.strptime(assignment.time, "%Y-%m-%dT%H:%M")
    except ValueError:
        return jsonify({'message': 'Invalid deadline format', 'marks': 0}), 400

    marks, message, _ = evaluate_script(compilation_success, deadline_time)
    return jsonify({'marks': marks, 'message': message})



@app.route('/logout')
def logout():
    session.clear()  # clear all session data
    flash("You have been logged out.")
    return redirect(url_for('login'))  # redirect to login page

@app.route('/subject/<int:sub_id>/assignments/create_script', methods=['GET', 'POST'])
def create_script_assignment(sub_id):
    subject = Subject.query.get_or_404(sub_id)

    if request.method == 'POST':
        title = request.form.get('title')
        deadline = request.form.get('deadline')
        total_marks = request.form.get('total_marks')
        questions = request.form.get('questions', '')
        rubric_selected = request.form.getlist('rubric_criteria')
        rubric = ', '.join(rubric_selected)
        compilation_time = request.form.get('compilation_time')
        compilation_time = int(compilation_time) if compilation_time and compilation_time.isdigit() else 0

        # Collect test cases dynamically
        testcases = []
        i = 1
        while True:
            input_key = f'test_input_{i}'
            output_key = f'test_output_{i}'
            if input_key in request.form and output_key in request.form:
                inp = request.form[input_key].strip()
                out = request.form[output_key].strip()
                if inp and out:
                    testcases.append({'input': inp, 'expected_output': out})
                i += 1
            else:
                break

        new_script = ScriptAssignment(
            title=title,
            deadline=deadline,
            total_marks=total_marks,
            questions=questions,
            rubric=rubric,
            compilation_time=compilation_time,
            testcases=json.dumps(testcases),
            sub_id=sub_id
        )
        db.session.add(new_script)
        db.session.commit()

        return redirect(url_for('subject_assignments', sub_id=sub_id))

    return render_template('create_script_assignment.html', subject=subject)
