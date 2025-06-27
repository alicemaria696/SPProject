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

select * from teacher;

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
