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

CREATE TABLE script_assignment (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  deadline DATETIME NOT NULL,
  total_marks INT NOT NULL,
  questions TEXT,
  testcases JSON, -- {"input": "...", "expected_output": "..."}
  rubric TEXT,     -- Checkboxes selected (e.g., Deadline, Test Cases, Compilation Time)
  compilation_time INT DEFAULT 0, -- in milliseconds
  sub_id INT NOT NULL,
  FOREIGN KEY (sub_id) REFERENCES subject(sub_id)
);

select * from script_assignment;

ALTER TABLE script_assignment 
ADD COLUMN function_name VARCHAR(100),
ADD COLUMN function_signature TEXT,
ADD COLUMN template_code TEXT,
ADD COLUMN language VARCHAR(20) DEFAULT 'c',
ADD COLUMN memory_limit INT DEFAULT 128000,
ADD COLUMN time_limit INT DEFAULT 2;

ALTER TABLE script_assignment MODIFY COLUMN testcases JSON;

CREATE TABLE script_submission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    script_assignment_id INT NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    
    -- Submission details
    submitted_code TEXT NOT NULL,
    language_used VARCHAR(20),
    submission_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Compilation results
    compilation_status VARCHAR(20), -- 'SUCCESS', 'FAILED'
    compilation_error TEXT,
    compilation_time DECIMAL(10,3),
    
    -- Test case results summary
    total_test_cases INT DEFAULT 0,
    passed_test_cases INT DEFAULT 0,
    failed_test_cases INT DEFAULT 0,
    
    -- Scoring
    total_marks INT DEFAULT 0,
    marks_obtained INT DEFAULT 0,
    
    -- Rubric-based scoring
    deadline_marks INT DEFAULT 0,    -- Marks for meeting deadline
    compilation_marks INT DEFAULT 0, -- Marks for successful compilation
    testcase_marks INT DEFAULT 0,    -- Marks for passing test cases
    
    -- Final evaluation
    final_status VARCHAR(20), -- 'PASS', 'FAIL'
    is_on_time BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (script_assignment_id) REFERENCES script_assignment (id) ON DELETE CASCADE
);

select * from script_submission;

CREATE TABLE test_case_result (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL,
    test_case_index INT NOT NULL,  -- Which test case (0, 1, 2...)
    input_data TEXT,
    expected_output TEXT,
    actual_output TEXT,
    status VARCHAR(20), -- 'PASSED', 'FAILED', 'ERROR', 'TIMEOUT'
    execution_time DECIMAL(10,3), -- Execution time in seconds
    memory_used INT, -- Memory used in KB
    error_message TEXT,  -- Error message if any
    
    FOREIGN KEY (submission_id) REFERENCES script_submission (id) ON DELETE CASCADE
);

select * from test_case_result;

CREATE INDEX idx_script_submission_student ON script_submission(student_id);
CREATE INDEX idx_script_submission_assignment ON script_submission(script_assignment_id);
CREATE INDEX idx_test_case_result_submission ON test_case_result(submission_id);
