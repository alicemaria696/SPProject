from app import db
from flask_login import UserMixin
from datetime import datetime

# Table for Admins and Students
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    reg_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'A' = Admin, 'S' = Student

# Table for Teachers (separate for managing emails and departments)
class Teacher(db.Model):
    __tablename__ = 'teacher'
    
    id = db.Column(db.Integer, primary_key=True)
    reg_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    class_ = db.Column(db.String(100), nullable=False)  # matches DB column `class_`
    password = db.Column(db.String(100), nullable=False)


class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.String(100), unique=True, nullable=False)  # e.g., '4 MCA A'

class Subject(db.Model):
    sub_id = db.Column(db.Integer, primary_key=True)
    s_name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Automatically set on creation
    time = db.Column(db.String(50), nullable=False)              # Deadline
    type = db.Column(db.String(20), nullable=False)              # theory/script
    total_marks = db.Column(db.Integer, nullable=False)
    sub_id = db.Column(db.Integer, db.ForeignKey('subject.sub_id'), nullable=False)