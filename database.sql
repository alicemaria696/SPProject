CREATE DATABASE assessment_system;

USE assessment_system;

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reg_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(10) NOT NULL
);

select * from user;


CREATE TABLE teacher (
  id INT AUTO_INCREMENT PRIMARY KEY,
  reg_id VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  department VARCHAR(100) NOT NULL,
  password VARCHAR(100) NOT NULL
);

 

select * from student;

CREATE TABLE student (
  id INT AUTO_INCREMENT PRIMARY KEY,
  reg_id VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  department VARCHAR(100) NOT NULL,
  class VARCHAR(100) NOT NULL,
  password VARCHAR(100) NOT NULL
);
ALTER TABLE student CHANGE `class` `class_` VARCHAR(100) NOT NULL;

select * from teacher;



CREATE TABLE class (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id VARCHAR(100) NOT NULL UNIQUE
);

select * from class;

CREATE TABLE subject (
    sub_id INT AUTO_INCREMENT PRIMARY KEY,
    s_name VARCHAR(100) NOT NULL,
    class_id INT NOT NULL,
    teacher_id INT NOT NULL,
    FOREIGN KEY (class_id) REFERENCES class(id),
    FOREIGN KEY (teacher_id) REFERENCES teacher(id)
);

select * from subject;

CREATE TABLE assignment (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  time VARCHAR(50) NOT NULL,
  type VARCHAR(20) NOT NULL,
  total_marks INT NOT NULL,
  sub_id INT NOT NULL,
  FOREIGN KEY (sub_id) REFERENCES subject(sub_id)
);

ALTER TABLE assignment
ADD COLUMN questions TEXT,
ADD COLUMN rubric TEXT,
ADD COLUMN keywords TEXT;

select * from assignment;

CREATE TABLE submission (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id VARCHAR(50) NOT NULL,
  subject_name VARCHAR(100) NOT NULL,
  submitted_document VARCHAR(200) NOT NULL,
  upload_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE submission
ADD COLUMN assignment_id INT AFTER id,
ADD COLUMN marks INT AFTER upload_time,
ADD COLUMN status VARCHAR(50) AFTER marks,
ADD COLUMN on_time BOOLEAN AFTER status;


select * from submission;

CREATE TABLE result (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id INT NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    file_name VARCHAR(200) NOT NULL,
    total_matches INT,
    marks INT,
    status VARCHAR(50),
    on_time BOOLEAN,
    evaluated_at DATETIME,
    FOREIGN KEY (assignment_id) REFERENCES assignment(id)
);
