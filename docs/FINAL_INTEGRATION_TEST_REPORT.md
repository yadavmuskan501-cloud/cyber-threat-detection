# Sentinel AI – Final Integration Testing Report

**Project:** Sentinel AI – Cyber Threat Detection & Alerting System  
**Module:** Backend Authentication, RBAC and Integration Testing  
**Prepared By:** Muskan  
**Backend Framework:** FastAPI  
**Database:** SQLite  
**Testing Framework:** Pytest  
**API Testing Tools:** Postman and Swagger UI  
**Report Date:** 23 November 2026  

**Final Status:** Backend Security Integration Verified – Full System Integration Pending

---

## 1. Objective

The objective of integration testing is to verify that the Sentinel AI backend and frontend communicate correctly, JWT-based authentication protects API endpoints, and Role-Based Access Control (RBAC) prevents unauthorized access.

The testing activities focus on:

1. User registration and login.
2. JWT access token generation and validation.
3. Protected API endpoint access.
4. Role-based authorization for Analyst and Admin users.
5. Automated backend testing using Pytest.
6. Manual API testing using Postman and Swagger UI.
7. Documentation of integration testing evidence.

The report also documents the verification status of Jenkins CI, Docker and ML integration.

## 2. Integration Testing Results

| Test ID | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| INT-01 | Start FastAPI application | Server starts successfully | Application startup completed | PASS |
| INT-02 | Open frontend login page | Login page loads | HTTP 200 OK | PASS |
| INT-03 | Login and open dashboard | Dashboard opens successfully | Dashboard opened | PASS |
| INT-04 | Register a test account | HTTP 201 Created | HTTP 201 Created | PASS |
| INT-05 | Login through API | HTTP 200 and JWT generated | HTTP 200 OK and access token received | PASS |
| INT-06 | Access protected API without JWT | HTTP 401 Unauthorized | HTTP 401 Unauthorized | PASS |
| INT-07 | Access protected API with valid JWT | HTTP 200 OK | Authorized profile returned | PASS |
| INT-08 | Analyst accesses Admin API | HTTP 403 Forbidden | HTTP 403 Forbidden | PASS |
| INT-09 | Analyst accesses Admin-only user listing | HTTP 403 Forbidden | HTTP 403 Forbidden | PASS |
| INT-10 | Analyst accesses threats endpoint | HTTP 200 OK | Endpoint tested; exact response not recorded | VERIFIED – RESPONSE UNRECORDED |
| INT-11 | Execute backend automated tests | All 13 tests pass | 13 passed in previously recorded run | PASS |
| INT-12 | Jenkins pipeline execution | Successful CI build | Latest successful build not verified | PENDING |
| INT-13 | Docker image build | Image builds successfully | Build not independently verified | PENDING |
| INT-14 | ML prediction API integration | Valid prediction response | Not independently verified | PENDING |
| INT-15 | Complete frontend-to-ML workflow | Prediction displayed on frontend | Not independently verified | PENDING |

## 3. Backend API Testing

The following REST API endpoints were tested as part of the authentication and authorization module.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Authenticate user and generate JWT |
| GET | `/api/auth/me` | Retrieve authenticated user profile |
| GET | `/api/rbac/threats` | Access role-protected threats endpoint |
| GET | `/api/rbac/admin` | Restrict Admin-only functionality |
| GET | `/api/rbac/users` | Restrict Admin-only user listing |

### 3.1 User Registration

The registration endpoint was tested using Swagger UI.

**Verified Result:** HTTP 201 Created.

A new test account was successfully registered.

### 3.2 JWT Authentication

The login endpoint was tested using valid registered credentials.

The authentication workflow includes:

1. Submitting username and password.
2. Validating user credentials.
3. Generating a JWT access token.
4. Returning the access token to the client.
5. Using the token to access protected API endpoints.

**Verified Result:** HTTP 200 OK with JWT access token.

### 3.3 Protected API Access

The `/api/auth/me` endpoint was tested with a valid JWT token.

The backend successfully authenticated the user and returned the user profile.

**Verified Result:** HTTP 200 OK.

### 3.4 Unauthorized API Access

The protected profile endpoint was also tested without a JWT token.

The backend rejected the unauthenticated request.

**Verified Result:** HTTP 401 Unauthorized.

## 4. Role-Based Access Control Testing

Role-Based Access Control (RBAC) restricts API access according to the authenticated user's assigned role.

The following scenarios were tested:

| User Role | Endpoint | Expected Result |
|---|---|---|
| Analyst | `/api/rbac/threats` | Access allowed |
| Analyst | `/api/rbac/admin` | Access denied |
| Analyst | `/api/rbac/users` | Access denied |
| Unauthenticated User | `/api/auth/me` | Access denied |

### 4.1 Analyst Access Restriction

An Analyst user attempted to access the Admin-only endpoint.

The backend rejected the request with:

**HTTP 403 Forbidden**

### 4.2 Admin-only User Listing

An Analyst user attempted to access the Admin-only user listing endpoint.

The backend rejected the request with:

**HTTP 403 Forbidden**

These tests demonstrate that unauthorized users cannot access restricted administrative resources.

## 5. Automated Backend Testing Using Pytest

Pytest was used to automate backend API and security testing.

### 5.1 Test Command

The backend-only test command is:

```powershell
python -m pytest -v tests/test_api.py tests/test_auth.py tests/test_login.py tests/test_rbac.py
```

### 5.2 Previously Recorded Test Results

| Metric | Result |
|---|---|
| Total backend tests | 13 |
| Passed | 13 |
| Failed | 0 |

**Recorded Result: 13 passed, 0 failed.**

### 5.3 Test Coverage

The automated tests cover:

1. Application startup.
2. Protected API authentication.
3. Invalid JWT token rejection.
4. Expired JWT token rejection.
5. Successful user login.
6. Invalid login credentials.
7. Analyst role authorization.
8. Admin-only endpoint restrictions.
9. Unauthorized access handling.

Passing these tests confirms the functionality covered by the automated test cases.

It does not guarantee that every application feature or security vulnerability has been independently verified.

## 6. Manual API Testing Using Postman and Swagger UI

Manual API testing was conducted to verify backend functionality and authentication behavior.

### 6.1 Postman Testing

Postman was used to execute backend API requests and inspect HTTP responses.

The testing activities included:

- User registration.
- User login.
- JWT-protected API access.
- Analyst endpoint access.
- Restricted Admin API access.
- Unauthorized access testing.

Six Postman screenshots were uploaded to the GitHub repository as testing evidence.

### 6.2 Swagger UI Testing

Swagger UI was accessed using:

`http://127.0.0.1:8000/docs`

The following operations were demonstrated:

1. User registration.
2. Successful login.
3. JWT access token generation.
4. Bearer token authorization.
5. Protected profile access.
6. Analyst authorization restrictions.
7. Unauthorized access without a JWT token.

Swagger UI was used for interactive API execution and verification.

**Status: Core Authentication and Authorization Demonstration Completed.**

## 7. Testing Evidence

### 7.1 GitHub Testing Evidence

The following six Postman screenshots are stored in:

`docs/testing_evidence/`

1. `Screenshot 2026-11-23 175518.png`
2. `Screenshot 2026-11-23 175533.png`
3. `Screenshot 2026-11-23 175544.png`
4. `Screenshot 2026-11-23 175603.png`
5. `Screenshot 2026-11-23 175614.png`
6. `Screenshot 2026-11-23 175625.png`

The screenshots provide supporting evidence of manual API testing.

### 7.2 Additional Testing Evidence

- Pytest execution results.
- JWT authentication test results.
- Protected API access results.
- HTTP 401 Unauthorized response.
- HTTP 403 Forbidden response.
- Swagger UI API demonstration.
- GitHub testing-evidence Pull Request merge.

Sensitive credentials and JWT access tokens must remain hidden in all shared screenshots.

## 8. Jenkins CI and Docker Verification

The project contains a Jenkinsfile configured for the following stages:

1. GitHub repository checkout.
2. Project file verification.
3. Python environment verification.
4. Automated Pytest execution.
5. Docker availability checks.
6. Docker image build.

The Jenkinsfile has been reviewed, but the latest successful Jenkins execution and Docker image build have not been independently verified.

**Current Status: PENDING VERIFICATION**

Required evidence:

- Jenkins SUCCESS build screenshot.
- Jenkins console output.
- Successful automated test execution.
- Docker image build output.
- Build branch and commit ID.

## 9. ML Integration Verification

The ML prediction module is handled by the ML development workstream.

The following activities require independent verification:

1. ML prediction endpoint execution.
2. Backend integration with the trained model.
3. Valid prediction API response.
4. Invalid-input handling.
5. Frontend display of prediction results.
6. Complete frontend-to-ML workflow.

**Current Status: PENDING VERIFICATION**

Required evidence:

- ML prediction endpoint.
- Successful prediction response.
- Invalid-input response.
- Frontend prediction display.
- End-to-end integration evidence.

## 10. Limitations

The following limitations were identified during integration testing:

1. Automated tests verify only the scenarios included in the test suite.
2. Jenkins CI execution requires independent verification.
3. Docker image build evidence is pending.
4. ML prediction API integration has not been independently verified.
5. Complete frontend-to-ML workflow testing remains pending.
6. The exact latest response for the threats endpoint was not recorded.

These limitations should be addressed before declaring the complete application fully integrated.

## 11. Conclusion

The Sentinel AI backend authentication and authorization modules have undergone automated and manual testing.

The previously recorded backend Pytest execution showed 13 passing tests.

Manual API testing through Postman and Swagger UI demonstrated successful user registration, JWT generation, authenticated profile access, and rejection of unauthenticated requests.

Role-Based Access Control was also tested to verify restrictions on Analyst access to Admin-only resources.

The testing evidence and integration report are maintained in the project's GitHub repository.

The backend authentication and RBAC functionality has been verified for the documented scenarios. However, Jenkins CI, Docker image building, ML prediction integration and complete end-to-end application testing require further independent verification.

**Final Status: Backend Security Testing Verified — Full System Integration Pending**

---

**Prepared By:** Muskan  
**Project:** Sentinel AI – Cyber Threat Detection & Alerting System  
**Module:** Backend Authentication, RBAC and Integration Testing  
**Report Date:** 23 November 2026