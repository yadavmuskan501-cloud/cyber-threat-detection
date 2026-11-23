# Sentinel AI – Final Integration Testing Report

**Project:** Sentinel AI – Cyber Threat Detection & Alerting System  
**Module:** Backend Authentication, RBAC and Integration Testing  
**Prepared By:** Muskan  
**Testing Framework:** Pytest  
**API Testing Tools:** Postman and Swagger UI  
**Backend:** FastAPI  
**Database:** SQLite  
**Report Date:** 23 November 2026  
**Status:** Backend Security Integration Verified — Full System Integration Pending

---

## 1. Objective

The objective of integration testing is to verify that the Sentinel AI frontend and backend communicate correctly, JWT-based authentication protects API endpoints, and Role-Based Access Control (RBAC) restricts unauthorized access.

The testing process focuses on:

1. User registration and login functionality.
2. JWT access token generation and validation.
3. Authentication of protected API endpoints.
4. Role-based authorization for Analyst and Admin users.
5. Automated backend security testing using Pytest.
6. Manual API verification using Postman and Swagger UI.
7. Documentation of testing evidence and integration results.

This report also records the verification status of Jenkins CI, Docker and ML integration.

## 2. Integration Testing Results

| Test ID | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| INT-01 | Start FastAPI application | Server starts successfully | Application startup completed | PASS |
| INT-02 | Open frontend login page | Login page loads | HTTP 200 OK | PASS |
| INT-03 | Login and open dashboard | Successful navigation | Dashboard opened | PASS |
| INT-04 | Register a test account | HTTP 201 Created | HTTP 201 Created in Swagger UI | PASS |
| INT-05 | Login through API | HTTP 200 and JWT token | HTTP 200 OK and access token received | PASS |
| INT-06 | Access protected API without JWT | HTTP 401 Unauthorized | HTTP 401 Unauthorized | PASS |
| INT-07 | Access protected API with valid JWT | HTTP 200 OK | Authenticated profile returned | PASS |
| INT-08 | Analyst accesses Admin-only API | HTTP 403 Forbidden | Admin access restriction tested; exact latest response not independently recorded | PREVIOUSLY TESTED |
| INT-09 | Analyst accesses Admin-only user listing | HTTP 403 Forbidden | HTTP 403 Forbidden | PASS |
| INT-10 | Analyst accesses threats endpoint | HTTP 200 OK | Endpoint executed; latest response status not independently recorded | PREVIOUSLY TESTED |
| INT-11 | Run automated backend Pytest tests | All backend tests pass | 13 passed in previously verified backend test run; latest output not attached | PREVIOUSLY VERIFIED |
| INT-12 | Jenkins pipeline execution | Successful CI build | Jenkins SUCCESS evidence unavailable | PENDING |
| INT-13 | Docker image build | Image builds successfully | Docker build execution not independently verified | PENDING |
| INT-14 | ML prediction API integration | Prediction API returns valid results | Endpoint and model integration not verified | PENDING |
| INT-15 | Complete frontend-to-ML workflow | Threat detection results displayed | End-to-end workflow not verified | PENDING |

The integration testing results demonstrate that the backend authentication and authorization functionality has been tested successfully.

However, full-system integration cannot be declared complete until the remaining Jenkins, Docker, ML and end-to-end tests are independently verified.

## 3. Backend API Testing

The following backend endpoints were used to verify authentication and authorization functionality.

| Method | API Endpoint | Purpose | Expected HTTP Status |
|---|---|---|---|
| POST | `/api/auth/register` | Register a new user | 201 Created |
| POST | `/api/auth/login` | Authenticate user and generate JWT | 200 OK |
| GET | `/api/auth/me` | Retrieve authenticated user profile | 200 OK |
| GET | `/api/rbac/threats` | Access role-protected threats endpoint | 200 OK |
| GET | `/api/rbac/admin` | Restrict Admin-only functionality | 403 Forbidden for Analyst |
| GET | `/api/rbac/users` | Restrict Admin-only user listing | 403 Forbidden for Analyst |
| GET | `/api/auth/me` without JWT | Verify authentication enforcement | 401 Unauthorized |

### 3.1 JWT Authentication Testing

JWT authentication was tested through user registration, login and protected endpoint access.

The authentication workflow includes:

1. Registering a user through the registration API.
2. Authenticating the registered user through the login API.
3. Receiving a JWT access token after successful login.
4. Supplying the token using Bearer authentication.
5. Accessing protected API endpoints with the valid token.
6. Verifying that requests without authentication are rejected.

**Verified Results:**

- User registration returned HTTP 201 Created.
- Successful login returned HTTP 200 OK.
- A JWT access token was generated after login.
- Authenticated profile access was successful.
- Access without a JWT returned HTTP 401 Unauthorized.

**Status: PASS**

### 3.2 Role-Based Access Control Testing

RBAC restricts API access according to the authenticated user's role.

The application uses role-based authorization to distinguish permitted Analyst operations from restricted Admin operations.

The following authorization scenarios were tested:

| User Role | Endpoint | Expected Result |
|---|---|---|
| Analyst | `/api/rbac/threats` | Access allowed |
| Analyst | `/api/rbac/admin` | Access denied |
| Analyst | `/api/rbac/users` | Access denied |
| Unauthenticated | `/api/auth/me` | Access denied |

The user-listing endpoint returned HTTP 403 Forbidden for an Analyst account.

The Admin endpoint and threats endpoint were also exercised during testing. Their latest exact response codes should be confirmed from the final test evidence before marking those individual checks as independently verified.

**Status: PARTIALLY REVERIFIED**

## 4. Automated Backend Security Testing Using Pytest

Pytest was used to automate backend security testing and verify the behavior of authentication and authorization endpoints.

### 4.1 Testing Command

The backend-only test command is:

```powershell
python -m pytest -v tests/test_api.py tests/test_auth.py tests/test_login.py tests/test_rbac.py
```

### 4.2 Recorded Test Results

| Metric | Result |
|---|---|
| Previously verified backend tests | 13 |
| Previously passed | 13 |
| Previously failed | 0 |
| Latest backend-only run | Output confirmation pending |

The previously verified backend test suite completed with 13 passing tests.

The latest backend-only test execution should be documented with its terminal summary before the report is treated as final execution evidence.

### 4.3 Security Test Coverage

The automated tests cover:

1. Basic backend API functionality.
2. User authentication.
3. JWT token validation.
4. Invalid authentication credentials.
5. Expired or invalid JWT handling.
6. Role-based authorization.
7. Unauthorized access restrictions.

Passing automated tests confirms the behavior covered by those tests. It does not guarantee that every security vulnerability has been eliminated.

**Status: PREVIOUS BACKEND TEST RUN PASSED**

## 5. Manual API Testing Using Postman and Swagger UI

Manual API testing was conducted to validate backend functionality and demonstrate authentication and authorization behavior.

### 5.1 Postman Testing

Postman was used to execute API requests and inspect HTTP responses.

The tested scenarios included:

- User registration.
- User login.
- JWT-protected profile access.
- Analyst threats endpoint access.
- Restricted Admin API access.
- Restricted user-listing access.
- Access without authentication.

Six Postman API testing screenshots were uploaded to the project's GitHub repository as supporting evidence.

### 5.2 Swagger UI Testing

Swagger UI was accessed through:

`http://127.0.0.1:8000/docs`

Swagger was used to demonstrate:

1. User registration with HTTP 201 Created.
2. Successful login with HTTP 200 OK.
3. JWT access token generation.
4. Bearer token authentication.
5. Protected API access.
6. Role-based authorization restrictions.
7. Unauthorized access returning HTTP 401.

The Swagger demonstration verified the core backend authentication workflow.

**Status: CORE AUTHENTICATION DEMONSTRATION PASSED**

## 6. Jenkins CI and Docker Verification

The project contains a Jenkinsfile configured for:

1. GitHub repository checkout.
2. Project file verification.
3. Python environment verification.
4. Automated Pytest execution.
5. Docker availability checks.
6. Docker image build.

The Jenkinsfile was reviewed, but successful Jenkins pipeline execution and Docker image creation have not yet been independently verified.

**Current Status: PENDING VERIFICATION**

Required evidence:

- Jenkins SUCCESS build screenshot.
- Jenkins console output showing test execution.
- Docker image build success output.
- Build branch and commit ID.

The Jenkins and Docker implementation and execution evidence are handled by the DevOps workstream.

## 7. ML Integration Verification

The ML prediction module is handled by the ML development workstream.

At the time of this report, the following items have not been independently verified:

1. ML prediction endpoint execution.
2. Model integration with the backend.
3. Valid prediction API responses.
4. Invalid-input handling.
5. Frontend display of ML prediction results.
6. Complete frontend-to-ML workflow.

**Current Status: PENDING VERIFICATION**

Required evidence:

- Integrated ML prediction endpoint.
- Valid prediction API response.
- Invalid-input response.
- Frontend display of prediction results, if implemented.
- End-to-end integration test results.

## 8. Testing Evidence

### 8.1 Available Evidence

The project contains the following testing documentation and evidence:

- Previously recorded Pytest execution showing 13 passed tests.
- GitHub Pull Request #6 merge evidence.
- Backend security test files.
- Authentication and authorization test results.
- Postman API testing screenshots.
- Swagger UI live demonstration results.
- GitHub testing-evidence Pull Request merged into the main branch.

### 8.2 Postman Screenshot Evidence

Six Postman screenshots are stored in:

`docs/testing_evidence/`

The screenshot files are:

1. `Screenshot 2026-11-23 175518.png`
2. `Screenshot 2026-11-23 175533.png`
3. `Screenshot 2026-11-23 175544.png`
4. `Screenshot 2026-11-23 175603.png`
5. `Screenshot 2026-11-23 175614.png`
6. `Screenshot 2026-11-23 175625.png`

These files document manual API testing activities. Individual screenshot contents should be checked before assigning each file to a specific test case.

Sensitive information such as passwords and JWT access tokens must be redacted from shared evidence.

### 8.3 Pending Evidence

The following evidence is still required:

- Latest backend-only Pytest summary.
- Jenkins successful build.
- Docker image build.
- ML prediction integration.
- Complete end-to-end application demonstration.

## 9. Limitations

The following limitations were identified during integration testing:

1. Passing the backend automated tests verifies only the functionality covered by those tests.
2. Jenkins pipeline execution has not been independently verified.
3. Docker image build evidence is pending.
4. ML prediction integration has not been independently verified.
5. Complete frontend-to-ML workflow testing remains pending.
6. Latest backend-only Pytest output needs to be recorded.
7. Some manual authorization test responses require final evidence confirmation.

These limitations should be resolved or documented before declaring the complete system fully integrated.

## 10. Conclusion

The Sentinel AI backend authentication and authorization modules have undergone automated and manual security testing.

Previously verified backend Pytest execution showed 13 passing tests.

Manual testing using Postman and Swagger UI demonstrated successful user registration, login, JWT generation, authenticated API access, and rejection of unauthenticated requests.

Role-Based Access Control was also tested to verify restrictions on Analyst access to Admin-only endpoints.

Testing evidence and the integration testing report are maintained in the GitHub repository.

The backend authentication and RBAC functionality has been substantially verified. However, the latest backend test execution, Jenkins CI, Docker, ML integration and full end-to-end application workflow require final independent verification.

**Final Status: Backend Security Testing Verified — Full System Integration Pending**

---

**Prepared By:** Muskan  
**Project:** Sentinel AI – Cyber Threat Detection & Alerting System  
**Module:** Backend Authentication, RBAC and Integration Testing  
**Date:** 23 November 2026