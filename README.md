\# 🛡️ SENTINEL AI: Cyber Threat Detection \& Alerting System



An AI-driven cybersecurity platform designed to monitor real-time network telemetry, detect anomalous intrusion events, and provide automated threat mitigation with instant SOC alerting.



\## 🚀 Key Features

\- \*\*Analyst Authentication Portal\*\*: Secure JWT token authentication with Bcrypt password hashing and role-based access control (RBAC).

\- \*\*Live SOC Threat Console\*\*: Real-time telemetry feed displaying active DDoS, SQL Injection, and Brute Force attacks.

\- \*\*AI Anomaly Detection\*\*: Threat classification with confidence scores and severity indicators.

\- \*\*One-Click Firewall Mitigation\*\*: Instant attacker IP blocking and containment actions.



\## 🛠️ Tech Stack

\- \*\*Backend\*\*: Python 3.12, FastAPI, Uvicorn

\- \*\*Security \& Cryptography\*\*: Bcrypt, Python-Jose (JWT)

\- \*\*Frontend\*\*: HTML5, Tailwind CSS, JavaScript

\- \*\*Deployment \& Architecture\*\*: REST API, SOC Dashboard



\## ⚡ Quick Start



1\. \*\*Clone the repository\*\*:

&#x20;  ```bash

&#x20;  git clone https://github.com/YOUR\_USERNAME/cyber-threat-detection.git

&#x20;  cd cyber-threat-detection


## 🐳 Docker Containerization

SentinelAI is containerized using Docker to ensure consistent application deployment.

- **Base Image:** Python 3.12 Slim
- **Image Name:** `sentinelai:latest`
- **Container Port:** 8000
- **Application Server:** FastAPI with Uvicorn

### Build Docker Image

```bash
docker build -t sentinelai:latest .
```

### Run Docker Container

```bash
docker run -d --name sentinelai-container -p 8000:8000 sentinelai:latest
```

### Verify Container

```bash
docker ps
docker logs sentinelai-container
```

---

## ☸️ Kubernetes Deployment

SentinelAI is deployed locally using Kubernetes through Minikube. Kubernetes manages application replicas, service access, scaling, and pod recovery.

**Tools Used:**
- Docker Desktop
- Minikube v1.39.0
- kubectl v1.36.1
- Kubernetes v1.37.0

### Kubernetes Architecture

- **Deployment:** Manages SentinelAI application pods.
- **Replicas:** Two application instances are maintained.
- **Service:** NodePort service exposes the application on port 30080.
- **Container Image:** `sentinelai:latest`
- **Application Port:** 8000

### Kubernetes Configuration

The following configuration files are included:

```text
k8s/
├── deployment.yaml
└── service.yaml
```

### Deploy to Kubernetes

Start the Minikube cluster:

```bash
minikube start --driver=docker
```

Load the Docker image:

```bash
minikube image load sentinelai:latest
```

Apply Kubernetes configurations:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Verify deployment:

```bash
kubectl get deployments
kubectl get pods
kubectl get services
```

### Access SentinelAI

Start the Kubernetes service tunnel:

```bash
minikube service sentinelai-service --url
```

Open the generated URL in a browser.

Swagger API documentation is available at:

```text
<MINIKUBE_URL>/docs
```

### Kubernetes Scaling

Horizontal scaling was tested by increasing the number of application replicas from two to three:

```bash
kubectl scale deployment sentinelai-deployment --replicas=3
kubectl get pods -l app=sentinelai
```

Three running pods were successfully verified.

The deployment was subsequently restored to two replicas.

### Kubernetes Self-Healing

Pod recovery was tested by manually deleting one application pod:

```bash
kubectl delete pod <POD_NAME>
```

Kubernetes automatically created a replacement pod to maintain the desired replica count.

### ML API Verification on Kubernetes

The Random Forest prediction endpoint was successfully tested through Kubernetes using Swagger and port forwarding:

```bash
kubectl port-forward service/sentinelai-service 8001:8000
```

Swagger documentation:

```text
http://127.0.0.1:8001/docs
```

The authenticated ML prediction endpoint returned:

- HTTP Status: 200 OK
- Model: Random Forest
- Prediction: ATTACK
- Prediction Code: 1
- Confidence: 1.0

This verified successful ML model inference through the Kubernetes deployment.

---

## 🧪 Deployment Verification Summary

| Test | Result |
|---|---|
| Docker image build | Passed |
| Docker container startup | Passed |
| ML model loading inside Docker | Passed |
| Kubernetes deployment | Passed |
| Kubernetes service access | Passed |
| Two application replicas | Passed |
| Scaling from 2 to 3 replicas | Passed |
| Automatic pod replacement | Passed |
| Swagger accessibility through Kubernetes | Passed |
| Authenticated ML prediction through Kubernetes | Passed |
