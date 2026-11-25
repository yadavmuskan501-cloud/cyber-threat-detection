# Sentinel AI: Future Scope

Sentinel AI currently classifies a single network traffic record as BENIGN
or ATTACK using a Random Forest model (CICIDS2017, 78 features), served
through a JWT-protected FastAPI endpoint (`POST /api/ml/predict`) and shown
on a SOC dashboard. This document describes how the project can grow into a
full monitoring and response platform.

## 1. Live network traffic monitoring

**Today:** a user submits one record of 78 features and receives a prediction.

**Next:**
- Capture packets or flow records from a network interface (for example
  with CICFlowMeter or Zeek) and compute the same 78 features automatically.
- Stream the flows to the prediction service continuously instead of
  submitting them by hand.
- Add a batch endpoint (`POST /api/ml/predict/batch`) so many flows can be
  classified in one request.

## 2. Real-time threat alerts

**Prototype included:** `alerts.py` stores an alert whenever a prediction
is ATTACK, assigns a severity from the model's confidence, and lists recent
alerts. It is covered by `tests/test_alerts.py`. The prototype is
standalone and keeps its alerts in its own small SQLite file, so it does not
touch the main MongoDB database. Moving the storage to a MongoDB collection
is part of the integration step below.

| Confidence | Severity |
|---|---|
| 0.95 or higher | Critical |
| 0.85 to 0.95 | High |
| 0.70 to 0.85 | Medium |
| below 0.70 | Low |

**Next:**
- Connect the prototype to the API. Call `save_alert` after a successful
  prediction in `/api/ml/predict`, and return `list_alerts` from
  `/api/rbac/threats`, which currently returns an empty list.
- Push alerts to the dashboard live with WebSockets or Server-Sent Events.
- Send notifications by email, Slack or SMS for High and Critical alerts.

## 3. Automated threat response

**Today:** blocking an attacker is a manual action on the dashboard.

**Next:**
- Block the source IP automatically at the firewall when a Critical alert
  is raised, with an Analyst approval step for lower severities.
- Keep an audit log of every automated action, so responses can be reviewed
  and reversed.

## 4. Model and platform improvements

- Retrain on newer datasets and add multi-class prediction (DDoS, brute
  force, SQL injection) instead of only BENIGN or ATTACK.
- Compare Random Forest with other models and track accuracy, precision and
  recall for each attack type, not accuracy alone.
- Add a health check endpoint (service and model loaded) and use it for
  Kubernetes readiness and liveness probes, so traffic is only sent to pods
  that are ready. The current deployment already runs two replicas with
  resource limits.
- Add monitoring and metrics (request rates, prediction latency, alert
  counts) for the deployed application.
- Store alerts in MongoDB alongside the user data, and add retention rules
  so old alerts are archived automatically.

## How the alert prototype would be connected

This is the intended change, described here but not yet applied to
`main.py`:

```python
from alerts import save_alert, list_alerts

# inside predict_network_threat, after result = predict_threat(...)
save_alert(result, current_user["username"])

# inside view_threats, replacing "threats": []
"threats": list_alerts()
```

The same two functions would then be reimplemented on a MongoDB collection
(using `database.py`) so alerts live with the rest of the application data.
The function names and the severity rules stay the same, so the tests
carry over.
