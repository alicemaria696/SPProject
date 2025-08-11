from flask import json, render_template, request, redirect, url_for, flash, session
import json
import time
import requests
from app import app, db
from app.models import (Teacher, User, Student, Class, Subject, Assignment, 
                       Submission, Result, ScriptAssignment, ScriptSubmission, 
                       TestCaseResult)
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
    script_assignments = ScriptAssignment.query.filter_by(sub_id=sub_id).all()
    return render_template("assignment_dashboard.html", subject=subject, assignments=assignments, script_assignments=script_assignments)

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

@app.route('/studentdashboard')
def student_dashboard():
    student_reg_id = session.get('reg_id')
    student = Student.query.filter_by(reg_id=student_reg_id).first()
    class_id = Class.query.filter_by(class_id=student.class_).first().id
    subjects = Subject.query.filter_by(class_id=class_id).all()

    all_assignments = []
    
    for subject in subjects:
        # Regular assignments
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
                'questions': a.questions
            })
        
        # Script-based assignments
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
                'timestamp': sa.timestamp.strftime('%Y-%m-%d %H:%M') if sa.timestamp else 'N/A',
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
    
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    
    filepath = os.path.join(uploads_dir, filename)
    file.save(filepath)

    new_submission = Submission(
        assignment_id=assignment.id,
        student_id=student_id,
        subject_name=subject.s_name,
        submitted_document=filename,
        upload_time=datetime.now(),
        marks=0,
        status='Submitted',
        on_time=True
    )
    db.session.add(new_submission)
    db.session.commit()

    flash('Assignment uploaded successfully!')
    return redirect(url_for('studentdashboard'))

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
        try:
            nlp = spacy.load("en_core_web_sm")
            print("⚠️ Warning: Falling back to en_core_web_sm — semantic scoring may be weaker.")
        except:
            # If no spacy model is available, use basic evaluation
            nlp = None

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

    if nlp:
        doc = nlp(text.lower())
        words = [token.text for token in doc if token.is_alpha]
        word_freq = Counter(words)
        match_count = sum(word_freq.get(kw, 0) for kw in keywords)
        
        # Semantic scoring
        semantic_score = 0
        for kw in keywords:
            kw_doc = nlp(kw)
            similarities = [kw_doc.similarity(sent) for sent in doc.sents]
            if similarities and max(similarities) > 0.75:
                semantic_score += 1
        semantic_score = (semantic_score / len(keywords)) * 100 if keywords else 0
    else:
        # Basic text processing without spacy
        words = re.findall(r'\w+', text.lower())
        word_freq = Counter(words)
        match_count = sum(word_freq.get(kw, 0) for kw in keywords)
        semantic_score = 0

    keyword_score = min(match_count / max(len(keywords), 1), 1.0) * 100
    word_count = len(words)
    word_score = min(word_count / 100, 1.0) * 100

    try:
        deadline = datetime.strptime(assignment.time, "%Y-%m-%dT%H:%M")
    except ValueError:
        return jsonify({'error': 'Invalid deadline format'}), 400

    on_time = datetime.now() <= deadline
    deadline_score = 100 if on_time else 0

    # Simplified plagiarism check (just set to 0 for now)
    plagiarism_score = 0
    plagiarism_penalty = 0

    total_score = (keyword_score + word_score + deadline_score + semantic_score + plagiarism_penalty) / 4
    status = 'Pass' if total_score >= 50 else 'Fail'

    student_id = session.get('reg_id')
    subject = Subject.query.filter_by(sub_id=assignment.sub_id).first()

    # Update or create submission
    submission = Submission.query.filter_by(assignment_id=assignment.id, student_id=student_id).first()
    if submission:
        submission.marks = int(total_score)
        submission.status = status
        submission.on_time = on_time
        submission.upload_time = datetime.now()
    else:
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

    # Create or update result
    result = Result.query.filter_by(assignment_id=assignment.id, student_id=student_id).first()
    if result:
        result.total_matches = match_count
        result.marks = int(total_score)
        result.status = status
        result.on_time = on_time
        result.evaluated_at = datetime.now()
    else:
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
    regular_results = Result.query.join(Assignment, Result.assignment_id == Assignment.id)\
                          .join(Subject, Assignment.sub_id == Subject.sub_id)\
                          .filter(Subject.class_id == class_id)\
                          .order_by(Result.evaluated_at.desc()).all()
    
    # Get script assignment results
    script_results = ScriptSubmission.query.join(ScriptAssignment, ScriptSubmission.script_assignment_id == ScriptAssignment.id)\
                                          .join(Subject, ScriptAssignment.sub_id == Subject.sub_id)\
                                          .filter(Subject.class_id == class_id)\
                                          .order_by(ScriptSubmission.submission_time.desc()).all()
    
    # Create combined results for the "All Results" tab
    combined_results = []
    
    # Add regular assignment results
    for result in regular_results:
        combined_results.append({
            'student_id': result.student_id,
            'subject_name': result.subject_name,
            'assignment_title': result.assignment.title if result.assignment else 'N/A',
            'assignment_type': 'regular',
            'marks_obtained': result.marks,
            'total_marks': result.assignment.total_marks if result.assignment else 0,
            'status': result.status,
            'on_time': result.on_time,
            'submitted_at': result.evaluated_at if result.evaluated_at else datetime.now()
        })
    
    # Add script assignment results
    for script_result in script_results:
        combined_results.append({
            'student_id': script_result.student_id,
            'subject_name': script_result.subject_name,
            'assignment_title': script_result.script_assignment.title if script_result.script_assignment else 'N/A',
            'assignment_type': 'script',
            'marks_obtained': script_result.marks_obtained,
            'total_marks': script_result.total_marks,
            'status': script_result.final_status,
            'on_time': script_result.is_on_time,
            'submitted_at': script_result.submission_time if script_result.submission_time else datetime.now()
        })
    
    # Sort combined results by submission time (newest first)
    combined_results.sort(key=lambda x: x['submitted_at'], reverse=True)
    
    subjects = Subject.query.filter_by(class_id=class_id).all()
    
    return render_template('class_dashboard.html', 
                         regular_results=regular_results, 
                         script_results=script_results,
                         combined_results=combined_results,
                         subjects=subjects, 
                         class_id=class_id)

@app.route('/subject/<int:sub_id>/results')
def view_results(sub_id):
    """View all results for assignments in a subject"""
    subject = Subject.query.get_or_404(sub_id)
    
    # Get results for regular assignments
    regular_results = Result.query.join(Assignment, Result.assignment_id == Assignment.id)\
                                 .filter(Assignment.sub_id == sub_id)\
                                 .order_by(Result.evaluated_at.desc()).all()
    
    # Get results for script assignments
    script_results = ScriptSubmission.query.join(ScriptAssignment, ScriptSubmission.script_assignment_id == ScriptAssignment.id)\
                                          .filter(ScriptAssignment.sub_id == sub_id)\
                                          .order_by(ScriptSubmission.submission_time.desc()).all()
    
    return render_template('results.html', subject=subject, regular_results=regular_results, script_results=script_results)

def evaluate_script(compilation_success, deadline_time):
    on_time = datetime.now() <= deadline_time
    if compilation_success and on_time:
        return 100, "✅ Compilation Successful - Submitted on Time", True
    elif compilation_success:
        return 70, "✅ Compilation Successful - ❌ Deadline Missed", False
    else:
        return 0, "❌ Compilation Failed", False

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

@app.route('/subject/<int:sub_id>/assignments/create_script', methods=['GET', 'POST'])
def create_script_assignment(sub_id):
    subject = Subject.query.get_or_404(sub_id)

    if request.method == 'POST':
        try:
            title = request.form.get('title')
            language = request.form.get('language', 'c')
            deadline_str = request.form.get('deadline')
            total_marks = int(request.form.get('total_marks'))
            questions = request.form.get('questions', '')
            
            # Convert deadline string to datetime
            deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
            
            # Optional function template details
            function_name = request.form.get('function_name') or None
            return_type = request.form.get('return_type') or None
            template_code = request.form.get('template_code') or None
            
            # Execution limits
            time_limit = int(request.form.get('time_limit', 2))
            memory_limit = int(request.form.get('memory_limit', 128000))
            
            # Rubric criteria
            rubric_selected = request.form.getlist('rubric_criteria')
            rubric = ', '.join(rubric_selected)

            # Collect test cases dynamically
            testcases = []
            i = 1
            while True:
                input_key = f'test_input_{i}'
                output_key = f'test_output_{i}'
                weight_key = f'test_weight_{i}'
                hidden_key = f'test_hidden_{i}'
                
                if input_key in request.form and output_key in request.form:
                    inp = request.form[input_key].strip()
                    out = request.form[output_key].strip()
                    weight = int(request.form.get(weight_key, 10))
                    is_hidden = bool(request.form.get(hidden_key))
                    
                    if inp and out:
                        testcases.append({
                            'input': inp,
                            'expected_output': out,
                            'weight': weight,
                            'is_hidden': is_hidden,
                            'index': i-1
                        })
                    i += 1
                else:
                    break

            # Generate function signature if function details provided
            function_signature = None
            if function_name and return_type:
                function_signature = f"{return_type} {function_name}();"

            # Generate basic template if none provided but function details given
            if not template_code and function_name and return_type:
                if language.lower() == 'c':
                    template_code = f"""#include <stdio.h>
#include <stdlib.h>

{return_type} {function_name}() {{
    // Write your code here
    
}}"""
                elif language.lower() == 'cpp':
                    template_code = f"""#include <iostream>
using namespace std;

{return_type} {function_name}() {{
    // Write your code here
    
}}"""
                elif language.lower() == 'python':
                    template_code = f"""def {function_name}():
    # Write your code here
    pass"""
                elif language.lower() == 'java':
                    template_code = f"""public class Solution {{
    public static {return_type} {function_name}() {{
        // Write your code here
        
    }}
}}"""

            new_script = ScriptAssignment(
                title=title,
                deadline=deadline,
                total_marks=total_marks,
                questions=questions,
                function_name=function_name,
                function_signature=function_signature,
                template_code=template_code,
                language=language,
                testcases=testcases,
                rubric=rubric,
                time_limit=time_limit,
                memory_limit=memory_limit,
                sub_id=sub_id,
                timestamp=datetime.now()
            )
            db.session.add(new_script)
            db.session.commit()

            flash('Script assignment created successfully!')
            return redirect(url_for('subject_assignments', sub_id=sub_id))
            
        except Exception as e:
            flash(f'Error creating assignment: {str(e)}')
            return redirect(url_for('create_script_assignment', sub_id=sub_id))

    return render_template('create_script_assignment.html', subject=subject)

def get_language_id(language):
    """Get Judge0 language ID"""
    language_map = {
        'c': 50,         # C (GCC 9.2.0)
        'cpp': 54,       # C++ (GCC 9.2.0)
        'java': 62,      # Java (OpenJDK 13.0.1)
        'python': 71     # Python (3.8.1)
    }
    return language_map.get(language.lower(), 50)

def execute_test_case(complete_code, test_input, language, time_limit=2, memory_limit=128000):
    """Execute single test case using Judge0"""
    try:
        payload = {
            "source_code": complete_code,
            "language_id": get_language_id(language),
            "stdin": test_input,
            "cpu_time_limit": time_limit,
            "memory_limit": memory_limit,
            "wall_time_limit": time_limit + 1,
            "max_processes_and_or_threads": 30,
            "enable_per_process_and_thread_time_limit": False,
            "enable_per_process_and_thread_memory_limit": False,
            "max_file_size": 1024
        }
        
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "7d2f3e542amshe0fc0fe7f077e94p1e5b46jsn07418d37bf0f",  # Replace with your API key
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
        }
        
        response = requests.post(
            "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=false&wait=true", 
            json=payload, 
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            return {
                'status': 'ERROR',
                'error': f'Judge0 API error: {response.status_code}',
                'stdout': '',
                'stderr': response.text,
                'time': 0,
                'memory': 0
            }
        
        result = response.json()
        return {
            'status': 'SUCCESS' if result.get('status', {}).get('id') == 3 else 'ERROR',
            'stdout': result.get('stdout', '').strip(),
            'stderr': result.get('stderr', ''),
            'compile_output': result.get('compile_output', ''),
            'time': float(result.get('time', 0) or 0),
            'memory': int(result.get('memory', 0) or 0),
            'status_id': result.get('status', {}).get('id', 0),
            'status_description': result.get('status', {}).get('description', '')
        }
        
    except Exception as e:
        return {
            'status': 'ERROR',
            'error': f'Execution error: {str(e)}',
            'stdout': '',
            'stderr': str(e),
            'time': 0,
            'memory': 0
        }

def evaluate_script_submission(student_code, script_assignment):
    """Evaluate script submission against all test cases"""
    results = {
        'compilation_status': 'UNKNOWN',
        'compilation_error': '',
        'total_test_cases': len(script_assignment.testcases),
        'passed_test_cases': 0,
        'failed_test_cases': 0,
        'test_results': [],
        'marks_breakdown': {},
        'final_marks': 0,
        'final_status': 'FAIL'
    }
    
    # Check if submission is on time
    is_on_time = datetime.now() <= script_assignment.deadline
    
    # Simple test to check compilation
    simple_test = {
        'input': '5\n',
        'expected_output': '5'
    }
    
    compile_result = execute_test_case(
        student_code, 
        simple_test['input'], 
        script_assignment.language,
        script_assignment.time_limit,
        script_assignment.memory_limit
    )
    
    results['compilation_status'] = 'SUCCESS' if compile_result['status'] == 'SUCCESS' else 'FAILED'
    results['compilation_error'] = compile_result.get('stderr', '') or compile_result.get('compile_output', '')
    
    if results['compilation_status'] == 'FAILED':
        results['marks_breakdown'] = {
            'deadline_marks': 30 if is_on_time else 0,
            'compilation_marks': 0,
            'testcase_marks': 0
        }
        results['final_marks'] = results['marks_breakdown']['deadline_marks']
        return results
    
    # If compilation successful, run all test cases
    passed_count = 0
    total_test_weight = sum(tc.get('weight', 10) for tc in script_assignment.testcases)
    earned_test_weight = 0
    
    for i, test_case in enumerate(script_assignment.testcases):
        test_result = execute_test_case(
            student_code,
            test_case['input'],
            script_assignment.language,
            script_assignment.time_limit,
            script_assignment.memory_limit
        )
        
        # Compare outputs
        expected = test_case['expected_output'].strip()
        actual = test_result['stdout'].strip()
        
        test_passed = (expected == actual and test_result['status'] == 'SUCCESS')
        
        if test_passed:
            passed_count += 1
            earned_test_weight += test_case.get('weight', 10)
        
        results['test_results'].append({
            'test_case_index': i,
            'input_data': test_case['input'],
            'expected_output': expected,
            'actual_output': actual,
            'status': 'PASSED' if test_passed else 'FAILED',
            'execution_time': test_result['time'],
            'memory_used': test_result['memory'],
            'error_message': test_result.get('stderr', '') if not test_passed else '',
            'weight': test_case.get('weight', 10),
            'is_hidden': test_case.get('is_hidden', False)
        })
    
    results['passed_test_cases'] = passed_count
    results['failed_test_cases'] = len(script_assignment.testcases) - passed_count
    
    # Calculate marks based on rubric
    testcase_score = (earned_test_weight / total_test_weight * 50) if total_test_weight > 0 else 0
    
    results['marks_breakdown'] = {
        'deadline_marks': 30 if is_on_time else 0,
        'compilation_marks': 20,  # Full marks for successful compilation
        'testcase_marks': int(testcase_score)
    }
    
    results['final_marks'] = sum(results['marks_breakdown'].values())
    results['final_status'] = 'PASS' if results['final_marks'] >= 50 else 'FAIL'
    
    return results

@app.route('/evaluate_script', methods=['POST'])
def evaluate_script_enhanced():
    """Enhanced script evaluation with LeetCode-style test cases"""
    data = request.get_json()
    assignment_id = data.get("assignment_id")
    student_code = data.get("student_code", "")
    
    # For backwards compatibility, also handle the old format
    if not student_code and 'compilation_success' in data:
        compilation_success = data.get("compilation_success")
        assignment = Assignment.query.get(assignment_id)
        if assignment:
            try:
                deadline_time = datetime.strptime(assignment.time, "%Y-%m-%dT%H:%M")
            except ValueError:
                return jsonify({'message': 'Invalid deadline format', 'marks': 0}), 400
            marks, message, _ = evaluate_script(compilation_success, deadline_time)
            return jsonify({'marks': marks, 'message': message})
    
    # New enhanced evaluation
    script_assignment = ScriptAssignment.query.get(assignment_id)
    if not script_assignment:
        return jsonify({'message': 'Script assignment not found', 'marks': 0}), 404
    
    if not student_code:
        return jsonify({'message': 'No code provided', 'marks': 0}), 400
    
    # Evaluate the submission
    evaluation_results = evaluate_script_submission(student_code, script_assignment)
    
    # Save submission to database
    student_id = session.get('reg_id')
    if student_id:
        submission = ScriptSubmission(
            script_assignment_id=script_assignment.id,
            student_id=student_id,
            subject_name=Subject.query.get(script_assignment.sub_id).s_name,
            submitted_code=student_code,
            language_used=script_assignment.language,
            submission_time=datetime.now(),
            compilation_status=evaluation_results['compilation_status'],
            compilation_error=evaluation_results['compilation_error'],
            total_test_cases=evaluation_results['total_test_cases'],
            passed_test_cases=evaluation_results['passed_test_cases'],
            failed_test_cases=evaluation_results['failed_test_cases'],
            total_marks=script_assignment.total_marks,
            marks_obtained=evaluation_results['final_marks'],
            deadline_marks=evaluation_results['marks_breakdown']['deadline_marks'],
            compilation_marks=evaluation_results['marks_breakdown']['compilation_marks'],
            testcase_marks=evaluation_results['marks_breakdown']['testcase_marks'],
            final_status=evaluation_results['final_status'],
            is_on_time=datetime.now() <= script_assignment.deadline
        )
        
        db.session.add(submission)
        db.session.flush()  # Get the submission ID
        
        # Save individual test case results
        for test_result in evaluation_results['test_results']:
            tc_result = TestCaseResult(
                submission_id=submission.id,
                test_case_index=test_result['test_case_index'],
                input_data=test_result['input_data'],
                expected_output=test_result['expected_output'],
                actual_output=test_result['actual_output'],
                status=test_result['status'],
                execution_time=test_result['execution_time'],
                memory_used=test_result['memory_used'],
                error_message=test_result['error_message']
            )
            db.session.add(tc_result)
        
        db.session.commit()
    
    return jsonify({
        'marks': evaluation_results['final_marks'],
        'message': f"Compilation: {evaluation_results['compilation_status']}, "
                  f"Test Cases: {evaluation_results['passed_test_cases']}/{evaluation_results['total_test_cases']} passed",
        'compilation_status': evaluation_results['compilation_status'],
        'test_results': evaluation_results['test_results'],
        'marks_breakdown': evaluation_results['marks_breakdown']
    })

# Add this route to provide template code to students
@app.route('/get_script_template/<int:assignment_id>')
def get_script_template(assignment_id):
    """Provide template code for script assignments"""
    script_assignment = ScriptAssignment.query.get(assignment_id)
    if not script_assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    
    return jsonify({
        'template_code': script_assignment.template_code or '',
        'function_name': script_assignment.function_name or '',
        'language': script_assignment.language,
        'function_signature': script_assignment.function_signature or ''
    })
