# Sentinel AI – Cyber Threat Detection & Alerting System
## Software Testing Report

**Project:** Sentinel AI – Cyber Threat Detection & Alerting System  
**Module:** Backend Authentication and Role-Based Access Control (RBAC)  
**Testing Framework:** Pytest  
**Backend Framework:** FastAPI  
**Programming Language:** Python  
**Database:** SQLite  
**Testing Type:** API Testing, Authentication Testing, Authorization Testing, Security Testing  
**Tested By:** Muskan (Backend Security & Testing)

---

## 1. Introduction

Sentinel AI is a cybersecurity capstone project designed to support cyber threat detection and alerting.

This report documents the automated testing performed on the backend authentication and Role-Based Access Control (RBAC) modules.

The purpose of testing is to verify that authentication endpoints behave correctly, JWT tokens are validated, and access to protected API endpoints is restricted according to user roles.

## 2. Testing Objectives

The main objectives are:

1. Verify that the FastAPI application starts successfully.
2. Validate user login functionality.
3. Verify JWT-based authentication.
4. Reject invalid and expired authentication tokens.
5. Restrict unauthenticated access to protected endpoints.
6. Verify Role-Based Access Control (RBAC).
7. Ensure Analyst users cannot access Admin-only endpoints.
8. Prevent users from obtaining Admin privileges through public registration.

## 3. Testing Environment

| Component | Technology |
|---|---|
| Programming Language | Python 3.12.6 |
| Backend Framework | FastAPI |
| Database | SQLite |
| Authentication | JWT |
| Password Hashing | bcrypt |
| Testing Framework | Pytest |
| API Testing | FastAPI TestClient |
| Development Environment | Visual Studio Code |
| Version Control | Git and GitHub |
| Operating System | Windows |

## 4. Test Cases

### 4.1 Basic API Testing

| Test ID | Test Case | Expected Result | Status |
|---|---|---|---|
| TC-01 | Verify FastAPI application startup | Application responds successfully | PASS |
| TC-02 | Access protected profile without authentication | Request is rejected | PASS |

### 4.2 JWT Authentication Testing

| Test ID | Test Case | Expected Result | Status |
|---|---|---|---|
| TC-03 | Access profile using invalid JWT | Authentication is rejected | PASS |
| TC-04 | Access profile using expired JWT | Expired token is rejected | PASS |
| TC-05 | Login with valid credentials | Login succeeds and JWT is returned | PASS |
| TC-06 | Login with incorrect password | Login request is rejected | PASS |

### 4.3 Role-Based Access Control Testing

| Test ID | Test Case | Expected Result | Status |
|---|---|---|---|
| TC-07 | Analyst accesses threats endpoint | Access permitted | PASS |
| TC-08 | Analyst accesses Admin endpoint | HTTP 403 Forbidden | PASS |
| TC-09 | User attempts Admin role assignment during registration | User remains Analyst | PASS |
| TC-10 | Admin accesses Admin endpoint | Access permitted | PASS |

### 4.4 Additional Security Testing

| Test ID | Test Case | Expected Result | Status |
|---|---|---|---|
| TC-11 | Access Admin endpoint without authentication | Access rejected | PASS |
| TC-12 | Access threats endpoint without authentication | Access rejected | PASS |
| TC-13 | Analyst attempts