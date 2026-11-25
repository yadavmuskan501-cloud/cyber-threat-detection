# Sentinel AI: Conclusion

## Objective

Sentinel AI is a cyber threat detection and alerting system. Its main
objective is to detect malicious network traffic using machine learning and
present the results to security analysts through a secure dashboard.

## What was built

| Area | Result |
|---|---|
| Machine learning | Random Forest classifier trained on the cleaned CICIDS2017 dataset, with a test accuracy of 99.79% on 78 network traffic features. It returns BENIGN or ATTACK with a confidence score. |
| Backend | FastAPI service with a prediction endpoint that rejects missing or unknown features, and a MongoDB database for user accounts. |
| Security | JWT authentication, Bcrypt password hashing and role-based access control for Admin and Analyst users, with a required secret key, restricted CORS and XSS protection. |
| Frontend | Login, registration and a threat monitoring dashboard. |
| Testing | Swagger and Postman for manual API checks, Pytest for the API, authentication, RBAC, JWT and ML endpoint, and Selenium for browser tests. |
| DevOps | Git and GitHub with branches and pull requests, a Dockerfile for containerization, a Jenkins pipeline for CI/CD and Kubernetes manifests (two replicas, resource limits) for deployment. |

## Limitations

- The model classifies one record at a time and is not yet connected to live
  network traffic.
- It predicts BENIGN or ATTACK only, not the specific attack type.
- Accuracy was measured on one dataset. Real networks may behave
  differently, so results on live traffic should be evaluated separately.
- Blocking an attacker is a manual action.

## Future scope

Live traffic monitoring, real-time alerts and automated response are
described in [FUTURE_SCOPE.md](FUTURE_SCOPE.md), together with a tested
prototype of alert logging (`alerts.py`).

## Summary

The project shows that a machine learning model can be combined with secure
authentication, an API, a dashboard and an automated testing and deployment
pipeline to form the foundation of a threat detection platform.
