# PeoplePay360 – Backend

**PeoplePay360** is an HR and Payroll Management System designed to manage employees, contracts, attendance, time off, salary structures, payroll processing, payslips, and dashboard reporting.

The backend is built using **Django, Django REST Framework, and PostgreSQL**, with JWT-based authentication, role-based access control, automated payroll calculations, and PDF payslip generation.

---

## Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Backend Tech Stack](#backend-tech-stack)
* [Backend Architecture](#backend-architecture)
* [Core Backend Modules](#core-backend-modules)

  * [Employees](#1-employees)
  * [Departments](#2-departments)
  * [Work Schedules](#3-work-schedules)
  * [Contracts](#4-contracts)
  * [Attendance](#5-attendance)
  * [Time Off](#6-time-off)
  * [Salary Structures](#7-salary-structures)
  * [Salary Rules](#8-salary-rules)
  * [Payroll Calculation](#9-payroll-calculation)
  * [Payruns](#10-payruns)
  * [Payslips](#11-payslips)
  * [PDF Generation](#12-pdf-generation)
* [Authentication](#authentication)
* [User Roles and Permissions](#user-roles-and-permissions)
* [API Structure](#api-structure)
* [Dashboard API](#dashboard-api)
* [Self-Service APIs](#self-service-apis)
* [Database Configuration](#database-configuration)
* [Environment Variables](#environment-variables)
* [Backend Setup](#backend-setup)
* [Seed Data](#seed-data)
* [API Authentication Example](#api-authentication-example)
* [Payroll Processing Flow](#payroll-processing-flow)
* [Business Rules](#business-rules)
* [Admin Interface](#admin-interface)
* [Running Tests](#running-tests)
* [Django System Check](#django-system-check)
* [Project Design Principles](#project-design-principles)
* [Current Backend Status](#current-backend-status)
* [Frontend Integration](#frontend-integration)
* [License](#license)

---

## Overview

PeoplePay360 provides a centralized backend for HR and payroll operations.

The backend is responsible for:

* Employee and department management
* Employee contracts and work schedules
* Attendance tracking and overtime calculation
* Employee time-off management and approvals
* Salary structures and configurable salary rules
* Automated payroll calculations
* Payrun processing and validation
* Payslip generation and historical payroll records
* PDF payslip generation
* JWT authentication and role-based authorization
* HR and payroll dashboard reporting
* Employee self-service functionality

The application follows a Django application-based architecture. Business logic is separated into service modules, while API-specific functionality is handled by Django REST Framework views and serializers.

---

## Features

### Human Resource Management

* Employee profile management
* Department management
* Work schedule configuration
* Employment contracts
* Employee status management
* Employee-specific information and records

### Attendance Management

* Daily attendance records
* Check-in and check-out tracking
* Expected and worked hours
* Overtime calculation
* Attendance status tracking
* Attendance correction information

### Time-Off Management

* Configurable time-off types
* Employee leave allocations
* Time-off requests
* Request approval and rejection
* Available allocation tracking
* Automatic allocation updates for approved leave

### Payroll Management

* Configurable salary structures
* Fixed, percentage, and formula-based salary rules
* Salary rule dependencies and sequence ordering
* Automated gross salary and net salary calculation
* Payroll period management
* Payrun processing
* Payslip generation
* Historical salary calculation snapshots

### Authentication and Authorization

* JWT authentication
* Access and refresh tokens
* Role-based permissions
* Employee self-service access
* Protected HR and payroll endpoints

### Reporting

* HR and payroll dashboard
* Employee statistics
* Attendance statistics
* Time-off summaries
* Payroll summaries
* Monthly salary trends
* PDF payslip generation

---

## Backend Tech Stack

| Technology            | Purpose                               |
| --------------------- | ------------------------------------- |
| Python 3.13           | Backend programming language          |
| Django 5.2            | Backend web framework                 |
| Django REST Framework | REST API development                  |
| PostgreSQL 18         | Relational database                   |
| Simple JWT            | JWT authentication                    |
| Django CORS Headers   | Cross-origin resource sharing         |
| ReportLab             | PDF payslip generation                |
| Pytest                | Automated testing                     |
| Pytest-Django         | Django testing integration            |
| Redis                 | Optional infrastructure               |
| Celery                | Optional asynchronous task processing |

Redis and Celery are optional and are not required for the current backend implementation.

---

## Backend Architecture

The backend follows a modular Django architecture in which each application is responsible for a specific business domain.

```text
backend/
│
├── api/
│   ├── dashboard.py
│   ├── exceptions.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── attendance/
│   ├── models.py
│   ├── admin.py
│   ├── services.py
│   └── migrations/
│
├── contracts/
│   ├── models.py
│   ├── admin.py
│   ├── services.py
│   └── migrations/
│
├── employees/
│   ├── models.py
│   ├── admin.py
│   └── migrations/
│
├── payroll/
│   ├── models.py
│   ├── admin.py
│   ├── services.py
│   └── migrations/
│
├── reports/
│   ├── models.py
│   ├── views.py
│   └── migrations/
│
├── time_off/
│   ├── models.py
│   ├── admin.py
│   ├── services.py
│   └── migrations/
│
├── users/
│   ├── models.py
│   └── migrations/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
├── pytest.ini
└── requirements.txt
```

### Architecture Responsibilities

| Component     | Responsibility                                                                        |
| ------------- | ------------------------------------------------------------------------------------- |
| `api/`        | REST API endpoints, serializers, permissions, exceptions, and dashboard functionality |
| `employees/`  | Employee records and related information                                              |
| `contracts/`  | Employee contracts and contract-related business logic                                |
| `attendance/` | Attendance records and calculations                                                   |
| `time_off/`   | Leave requests, allocations, and approvals                                            |
| `payroll/`    | Salary structures, salary rules, payruns, payslips, and payroll calculations          |
| `reports/`    | Reporting functionality                                                               |
| `users/`      | User-related models                                                                   |
| `config/`     | Django project settings, URL configuration, and WSGI entry point                      |

Business logic that needs to be reused or tested is placed in service modules. API-specific behavior remains in DRF views and serializers.

---

# Core Backend Modules

## 1. Employees

The employee module acts as the central HR record for employees.

It manages:

* Employee number
* Personal information
* Contact information
* Job title
* Department
* Manager
* Employee type
* Hire date
* Termination date
* Work schedule
* Bank information
* Employee status

### Employee Statuses

| Status       | Description                     |
| ------------ | ------------------------------- |
| `ACTIVE`     | Employee is currently active    |
| `ON_LEAVE`   | Employee is on leave            |
| `TERMINATED` | Employee's employment has ended |

Employee records are connected to other HR and payroll modules, including contracts, attendance, and time-off management.

## 2. Departments

Departments organize employees into company departments.

Example departments used in the seed data:

* Engineering
* Human Resources
* Finance
* Marketing

Departments provide organizational information for employee management and dashboard reporting.

## 3. Work Schedules

Work schedules define the weekly working pattern of employees.

Each schedule can contain:

* Day of week
* Start time
* End time
* Break duration

The backend calculates working duration while validating that:

* End time is after start time.
* Break duration does not exceed the working duration.

Work schedules are used by attendance calculations and employee contracts.

## 4. Contracts

Contracts connect employees with their payroll and working configuration.

A contract contains:

* Employee
* Salary structure
* Work schedule
* Contract number
* Start date
* End date
* Contract type
* Base salary
* Currency
* Status
* Notes

The contract service determines which contract applies to an employee for a specific payroll period.

The backend also validates contract date ranges and prevents overlapping contracts.

## 5. Attendance

The attendance module records daily employee attendance.

Attendance records contain:

* Employee
* Work schedule
* Attendance date
* Check-in time
* Check-out time
* Expected hours
* Worked hours
* Overtime hours
* Attendance status
* Notes
* Correction information

### Attendance Statuses

| Status     | Description                               |
| ---------- | ----------------------------------------- |
| `PRESENT`  | Employee is present                       |
| `ABSENT`   | Employee is absent                        |
| `HALF_DAY` | Employee has a half-day attendance record |
| `LATE`     | Employee has a late attendance record     |
| `ON_LEAVE` | Employee is on leave                      |
| `HOLIDAY`  | The date is marked as a holiday           |

The backend calculates worked hours and overtime based on attendance information.

## 6. Time Off

The time-off module manages employee leave.

It supports:

* Time-off types
* Time-off allocations
* Time-off requests
* Approval
* Rejection
* Available allocation tracking

When an approved request consumes allocated leave, the corresponding allocation is updated.

Employees who are terminated cannot create new time-off requests.

## 7. Salary Structures

Salary structures define the collection of salary rules used during payroll calculation.

A salary structure contains:

* Code
* Name
* Description
* Currency
* Active status
* Salary rules

Example salary structure:

```text
MONTHLY-INR
```

Salary structures allow payroll calculations to use configurable salary components.

## 8. Salary Rules

Salary rules determine how individual payroll components are calculated.

### Supported Categories

| Category    | Purpose                      |
| ----------- | ---------------------------- |
| `BASIC`     | Basic salary component       |
| `ALLOWANCE` | Additional salary components |
| `GROSS`     | Gross salary calculation     |
| `DEDUCTION` | Salary deductions            |
| `NET`       | Net salary calculation       |

### Supported Calculation Types

| Type         | Description                             |
| ------------ | --------------------------------------- |
| `FIXED`      | Uses a fixed monetary amount            |
| `PERCENTAGE` | Calculates an amount using a percentage |
| `FORMULA`    | Calculates an amount using a formula    |

Salary rules support:

* Sequence ordering
* Fixed amounts
* Percentages
* Formula-based calculations
* Base rule dependencies
* Active and inactive rules

Rules are evaluated according to their configured sequence. Later rules can use values calculated by earlier rules.

Example salary calculation sequence:

```text
BASIC
  |
  v
HRA
  |
  v
GROSS
  |
  v
PF
  |
  v
NET
```

Formula-based rules are restricted to arithmetic expressions and previously calculated salary rule values.

## 9. Payroll Calculation

Payroll calculation is implemented in:

```text
payroll/services.py
```

### Calculation Flow

```text
Contract Base Salary
        |
        v
Salary Structure
        |
        v
Salary Rules
        |
        v
Rule Sequence
        |
        v
Calculated Salary Components
        |
        v
Gross Salary
        |
        v
Deductions
        |
        v
Net Salary
```

The payroll calculation service processes salary rules according to their configured sequence and calculates the corresponding salary components.

### Monetary Precision

* Money calculations use Python `Decimal` values.
* Monetary amounts are rounded to two decimal places.
* Formula-based rules can use previously calculated salary rule values.

This keeps payroll calculations separate from API-specific functionality.

## 10. Payruns

A payrun represents one payroll processing cycle.

A payrun contains:

* Name
* Salary structure
* Payroll period
* Payment date
* Selected employees
* Employee count
* Gross total
* Deduction total
* Net total
* Processing status

### Payrun Statuses

| Status      | Description               |
| ----------- | ------------------------- |
| `DRAFT`     | Payrun is in draft state  |
| `COMPUTED`  | Payroll has been computed |
| `VALIDATED` | Payrun has been validated |
| `PAID`      | Payrun is marked as paid  |
| `CANCELLED` | Payrun has been cancelled |

The payrun API supports selecting employees and processing their payroll for the defined period.

## 11. Payslips

A payslip represents the payroll result for one employee in a payrun.

A payslip stores:

* Employee
* Applicable contract
* Salary structure
* Payrun
* Payroll period
* Worked days
* Employee snapshot information
* Currency
* Gross amount
* Deduction amount
* Net amount
* Status
* Generation timestamp

### Payslip Statuses

| Status      | Description                |
| ----------- | -------------------------- |
| `DRAFT`     | Payslip is in draft state  |
| `FINALIZED` | Payslip has been finalized |
| `PAID`      | Payslip is marked as paid  |
| `CANCELLED` | Payslip has been cancelled |

Each payslip contains detailed salary lines.

### Payslip Lines

A payslip line stores:

* Salary rule
* Rule code
* Rule name
* Category
* Sequence
* Calculation base
* Calculated amount
* Description

This preserves the salary calculation history used to generate the payslip.

## 12. PDF Generation

PeoplePay360 supports payslip PDF generation using ReportLab.

The PDF generation layer uses the payslip and its calculated salary lines to produce a printable payroll document.

A generated payslip can contain:

* Employee details
* Payroll period
* Salary structure
* Worked days
* Earnings
* Deductions
* Net salary
* Salary rule breakdown

PDF generation is kept separate from the core salary calculation logic.

---

# Authentication

The backend uses JWT authentication through Django REST Framework Simple JWT.

### Authentication Endpoints

| Method | Endpoint             | Description                               |
| ------ | -------------------- | ----------------------------------------- |
| `POST` | `/api/auth/login/`   | Authenticate a user and obtain JWT tokens |
| `POST` | `/api/auth/refresh/` | Refresh an access token                   |

### Login Response

A successful login returns an access token and a refresh token.

```json
{
  "refresh": "<refresh-token>",
  "access": "<access-token>"
}
```

### Authenticated Requests

Authenticated API requests use the Bearer token in the `Authorization` header.

```http
Authorization: Bearer <access-token>
```

---

# User Roles and Permissions

PeoplePay360 supports role-based access control through custom Django REST Framework permission classes.

### Supported Roles

| Role                 | Description                              |
| -------------------- | ---------------------------------------- |
| `EMPLOYEE`           | Employee self-service access             |
| `HR_MANAGER`         | HR management access                     |
| `HR_PAYROLL_USER`    | HR and payroll processing access         |
| `HR_PAYROLL_MANAGER` | Broader HR and payroll management access |
| `ADMIN`              | Full system access                       |

## RBAC Overview

### Employee

Employees can access their own relevant information and self-service functionality.

Examples include:

* Own employee profile
* Own attendance
* Own time-off requests

### HR Manager

HR Managers have access to core HR management functionality, including employee and HR-related management operations.

### HR Payroll User

HR Payroll Users have HR access along with payroll processing capabilities.

They can work with:

* Payruns
* Payslips

Salary structures and salary rules remain available as read-oriented payroll configuration.

### HR Payroll Manager

HR Payroll Managers have broader HR and payroll management permissions.

### Admin

Admins have full system access.

Role-based permissions control access to HR and payroll operations according to the user's role.

---

# API Structure

The main API routes are grouped under:

```text
/api/
```

### Core Endpoint Groups

| Endpoint                     | Module               |
| ---------------------------- | -------------------- |
| `/api/auth/`                 | Authentication       |
| `/api/departments/`          | Departments          |
| `/api/employees/`            | Employees            |
| `/api/work-schedules/`       | Work schedules       |
| `/api/work-schedule-days/`   | Work schedule days   |
| `/api/contracts/`            | Contracts            |
| `/api/attendance/`           | Attendance           |
| `/api/time-off-types/`       | Time-off types       |
| `/api/time-off-allocations/` | Time-off allocations |
| `/api/time-off-requests/`    | Time-off requests    |
| `/api/salary-structures/`    | Salary structures    |
| `/api/salary-rules/`         | Salary rules         |
| `/api/payruns/`              | Payruns              |
| `/api/payslips/`             | Payslips             |
| `/api/dashboard/`            | Dashboard            |

The API is built using Django REST Framework, with custom serializers, views, and permission classes.

---

# Dashboard API

The dashboard endpoint provides aggregated HR and payroll information.

### Endpoint

```http
GET /api/dashboard/
```

### Example Response

```json
{
  "employees": {
    "total": 0,
    "active": 0,
    "on_leave": 0
  },
  "payroll": {
    "total_net_paid": 0,
    "payslips_generated": 0,
    "average_salary": 0
  },
  "attendance": {
    "total": 0,
    "present": 0,
    "absent": 0,
    "half_day": 0,
    "late": 0,
    "on_leave": 0,
    "health_percentage": 0
  },
  "time_off": {
    "approved": 0,
    "pending": 0,
    "rejected": 0
  },
  "departments": [],
  "monthly_salary_trend": []
}
```

The dashboard provides:

* Total, active, and on-leave employee counts
* Payroll totals and salary averages
* Generated payslip statistics
* Attendance summaries
* Attendance health percentage
* Time-off request summaries
* Department information
* Monthly salary trends

Dashboard data is calculated directly from the current database records.

---

# Self-Service APIs

The backend provides employee self-service endpoints for authenticated employees.

These endpoints allow employees to access their own:

* Employee information
* Attendance information
* Time-off information

The backend determines the employee profile associated with the authenticated user.

Self-service functionality is protected by authentication and role-based permissions.

---

# Database Configuration

PeoplePay360 uses **PostgreSQL 18** as its relational database.

### Default Development Configuration

```env
DB_NAME=peoplepay360
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD
DB_HOST=localhost
DB_PORT=5432
```

Django handles database schema changes through migrations.

---

# Environment Variables

Create a `.env` file inside the backend directory.

### Example `.env`

```env
SECRET_KEY=django-insecure-peoplepay360-development-key
DEBUG=True

DB_NAME=peoplepay360
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/0
```

### Environment Variable Reference

| Variable      | Purpose                               |
| ------------- | ------------------------------------- |
| `SECRET_KEY`  | Django secret key                     |
| `DEBUG`       | Enables or disables Django debug mode |
| `DB_NAME`     | PostgreSQL database name              |
| `DB_USER`     | PostgreSQL username                   |
| `DB_PASSWORD` | PostgreSQL password                   |
| `DB_HOST`     | PostgreSQL server hostname            |
| `DB_PORT`     | PostgreSQL server port                |
| `REDIS_URL`   | Optional Redis connection URL         |

**Production configuration:** Replace the development secret key and database credentials with secure values. Disable debug mode in production and keep credentials out of version control.

---

# Backend Setup

The following instructions describe the local development setup on Windows using PowerShell.

## Prerequisites

Install the following:

* Python 3.13
* PostgreSQL 18
* Git
* pip

## 1. Clone the Repository

```powershell
git clone <YOUR_REPOSITORY_URL>
```

Navigate to the backend directory:

```powershell
cd PeoplePay/backend
```

Replace the repository URL and directory name with the actual values for your project.

## 2. Create a Virtual Environment

```powershell
python -m venv venv
```

## 3. Activate the Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

## 4. Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure Environment Variables

Create a `.env` file inside the backend directory.

```text
backend/.env
```

Configure the PostgreSQL connection and Django environment variables as described in the [Environment Variables](#environment-variables) section.

## 6. Create the PostgreSQL Database

Create a PostgreSQL database named:

```text
peoplepay360
```

Make sure the database credentials match the values in your `.env` file.

## 7. Apply Database Migrations

```powershell
python manage.py migrate
```

## 8. Create an Admin User

```powershell
python manage.py createsuperuser
```

Follow the Django prompts to create the administrator account.

## 9. Start the Development Server

```powershell
python manage.py runserver
```

The backend development server will be available at:

```text
http://127.0.0.1:8000/
```

---

# Seed Data

The project includes demo data for development and testing.

The seeded environment includes:

* Departments
* Work schedules
* Employees
* Contracts
* Attendance records
* Time-off types
* Time-off allocations
* Salary structures
* Salary rules
* Demo users

### Demo Employee Users

```text
aarav
riya
dev
```

### HR Manager

```text
neha
```

### HR Payroll Manager

```text
karan
```

### Development Password

```text
PeoplePay@123
```

> **Security warning:** These credentials are for local development and demonstration purposes only. They must not be used in production.

---

# API Authentication Example

The following example uses PowerShell to authenticate and access the dashboard API.

## 1. Login

```powershell
$login = Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/auth/login/" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"username":"karan","password":"PeoplePay@123"}'
```

## 2. Store the Access Token

```powershell
$token = $login.access
```

## 3. Call an Authenticated Endpoint

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/dashboard/" `
  -Method Get `
  -Headers @{
      Authorization = "Bearer $token"
  }
```

The authenticated request sends the access token using the Bearer authentication scheme.

---

# Payroll Processing Flow

The complete payroll workflow is:

```text
Employee
   |
   v
Contract
   |
   v
Salary Structure
   |
   v
Salary Rules
   |
   v
Payrun
   |
   v
Select Employees
   |
   v
Calculate Payroll
   |
   v
Payslip
   |
   v
Payslip Lines
   |
   v
Validate
   |
   v
Paid
```

### Payroll Workflow Description

1. An employee is associated with an applicable employment contract.
2. The contract references a salary structure and work schedule.
3. Salary rules define the salary components and calculation methods.
4. A payrun is created for a specific payroll period.
5. Employees are selected for the payrun.
6. Payroll is calculated using the applicable contracts and salary rules.
7. Payslips and their salary lines preserve the calculation results.
8. The payrun and payslips proceed through the relevant processing statuses.

Historical payroll information is preserved through payslips and their salary-line snapshots.

---

# Business Rules

Important business rules are implemented in backend application logic rather than relying only on frontend validation.

The backend enforces the following rules:

* Contract periods cannot be invalid.
* Contracts cannot overlap for the same employee.
* Salary rules must contain the required calculation information.
* Percentage rules require a base rule.
* Formula rules require a formula.
* Salary rules execute in sequence order.
* Payroll amounts use decimal arithmetic.
* Attendance checkout cannot occur before check-in.
* Time-off requests validate their date ranges.
* Approved time off affects allocation usage.
* Terminated employees cannot create time-off requests.
* A payslip belongs to a specific payrun and employee.
* Payroll history is preserved through payslip records.

These rules help maintain consistency across HR and payroll operations.

---

# Admin Interface

Django Admin is used for backend administration and data management.

Start the development server:

```powershell
python manage.py runserver
```

Open the following URL:

```text
http://127.0.0.1:8000/admin/
```

Log in using the superuser credentials created with `createsuperuser`.

The admin interface provides management access to the configured Django applications and their models.

---

# Running Tests

The backend uses Pytest and Pytest-Django for automated testing.

### Run the Complete Test Suite

```powershell
pytest -q
```

### Test Coverage

The test suite covers core business logic and API functionality, including:

* Authentication
* Role-based access control (RBAC)
* Employee APIs
* HR APIs
* Attendance
* Time off
* Salary structures
* Salary rules
* Payroll
* Payruns
* Payslips
* Dashboard functionality

### Current Backend Verification

```text
29 tests passed
0 issues found by Django system checks
```

These results reflect the documented backend verification.

---

# Django System Check

Before committing backend changes, run:

```powershell
python manage.py check
```

A successful result should look like:

```text
System check identified no issues
```

This command checks the Django project for common configuration and application issues.

---

# Project Design Principles

PeoplePay360 follows a simple, application-focused backend architecture.

The project intentionally avoids unnecessary complexity, including:

* Microservices
* Repository layers
* CQRS
* Event buses
* Excessive abstraction
* Separate service frameworks

Instead, the backend uses Django's built-in capabilities and application structure.

### Separation of Responsibilities

| Layer              | Responsibility                           |
| ------------------ | ---------------------------------------- |
| Django Models      | Database structure and relationships     |
| Service Modules    | Reusable business logic and calculations |
| DRF Serializers    | API data validation and serialization    |
| DRF Views          | API request handling                     |
| Permission Classes | Authentication and authorization rules   |
| Django Migrations  | Database schema changes                  |

This architecture keeps the backend modular and makes business logic easier to maintain and test.

---

# Current Backend Status

The following features are implemented in the documented backend.

| Feature                           | Status    |
| --------------------------------- | --------- |
| Django and PostgreSQL integration | Completed |
| Django Admin                      | Completed |
| Database migrations               | Completed |
| Seed/demo data                    | Completed |
| Employee management               | Completed |
| Departments                       | Completed |
| Work schedules                    | Completed |
| Contracts                         | Completed |
| Attendance                        | Completed |
| Time off                          | Completed |
| Salary structures                 | Completed |
| Salary rules                      | Completed |
| Payroll calculation               | Completed |
| Payruns                           | Completed |
| Payslips                          | Completed |
| JWT authentication                | Completed |
| Role-based access control         | Completed |
| Employee self-service APIs        | Completed |
| Dashboard API                     | Completed |
| PDF generation                    | Completed |
| Automated tests                   | Completed |
| Django system checks              | Completed |

### Optional Infrastructure

| Technology | Status   |
| ---------- | -------- |
| Redis      | Optional |
| Celery     | Optional |

Redis and Celery are not required for the current core backend workflow.

---

# Backend Verification

The backend has been verified using the following commands.

### Django System Check

```powershell
python manage.py check
```

### Automated Tests

```powershell
pytest -q
```

### Current Test Results

```text
29 passed
```

The dashboard API was also manually verified using JWT authentication.

```http
GET /api/dashboard/
```

The endpoint returned successful employee, payroll, attendance, time-off, department, and salary-trend data during the documented verification.

---

# Frontend Integration

With the backend API complete, development moves to frontend integration.

The Next.js frontend will consume the Django REST APIs for:

* Authentication
* Dashboard
* Employees
* Departments
* Contracts
* Attendance
* Time off
* Salary structures
* Salary rules
* Payruns
* Payslips

The frontend will provide the user-facing HR and payroll interface, while Django remains responsible for:

* Authentication
* Authorization
* Business rules
* Payroll calculations
* Database operations
* API responses
* Payslip generation

---

# License

PeoplePay360 is currently developed as a software engineering project and demonstration system.
