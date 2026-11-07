# DIAGNOCARE — Diabetes Risk Monitoring Platform

**A healthcare monitoring platform for tracking glucose trends, managing patient health records, and supporting diabetes risk monitoring through machine learning.**

> DIAGNOCARE is a monitoring and decision-support prototype for individuals already diagnosed with diabetes. It is not a diabetes diagnostic or prediction system.

## Overview

DIAGNOCARE is a healthcare application designed to help users monitor their diabetes-related health indicators over time. Its backend integrates health-record workflows, glucose monitoring, medication management, reminders, reporting, and machine-learning-assisted risk monitoring through a Flask REST API.

The system combines temporal feature engineering with an XGBoost model and SHAP-based explainability to support more interpretable risk-monitoring outputs.

## Key Features

- **Authentication & User Profiles** — JWT-based authentication and profile management.
- **Health Metrics Management** — recording and retrieving patient health measurements.
- **Glucose Monitoring** — glucose recording, monitoring, and trend-related workflows.
- **Medication Management** — medication reminder creation and management.
- **Appointment & Reminder Management** — calendar and reminder functionality.
- **Reports & Documents** — monthly health reports and PDF reporting workflows.
- **ML-Assisted Risk Monitoring** — temporal feature engineering and XGBoost-based risk assessment.
- **Explainable AI** — SHAP-based explanations for model outputs.
- **REST API Architecture** — modular Flask routes and service-layer organization.

## System Architecture

```text
                 Flutter Client
                       |
                 REST API
                       |
               Flask Backend
                       |
       +---------------+----------------+
       |               |                |
 Authentication    Health Data       Management
       |            Monitoring        Services
       |               |                |
       +---------------+----------------+
                       |
               Service Layer
                       |
       +---------------+----------------+
       |               |                |
 Feature           Temporal          Reporting
 Engineering       XGBoost           Services
       |               |
       +------- SHAP Explanations -----+
                       |
                SQLAlchemy ORM
                       |
                 SQLite / DB
```

## Machine Learning Pipeline

The backend incorporates a temporal machine-learning pipeline for diabetes risk monitoring.

1. Health measurements are collected through application workflows.
2. Temporal features are constructed from patient measurement history.
3. The feature pipeline prepares inputs for the trained XGBoost model.
4. The model produces risk-monitoring outputs.
5. SHAP supports interpretation of contributing model features.
6. Monitoring outputs can be incorporated into application workflows.

**Important:** Model outputs are experimental decision-support signals and are not clinically validated diagnoses.

## Technology Stack

| Category | Technologies |
|---|---|
| Backend | Python, Flask, Flask-RESTful |
| API | REST, Flask Blueprints, Flask-CORS |
| Database | SQLAlchemy, SQLite |
| Authentication | Flask-JWT-Extended |
| Machine Learning | XGBoost, scikit-learn |
| Explainability | SHAP |
| Data Processing | pandas, NumPy |
| Model Utilities | joblib |
| Deployment | Gunicorn |

## Project Structure

```text
diagnocare-backend/
├── app.py
├── config.py
├── models.py
├── predict_temporal.py
├── routes/
│   ├── authentication
│   ├── metrics
│   ├── glucose monitoring
│   ├── calendar
│   ├── medication
│   ├── reminders
│   ├── reports
│   └── documents
├── services/
│   ├── feature engineering
│   ├── ML inference
│   ├── trends and insights
│   ├── reminders
│   └── reporting
├── utils/
├── requirements.txt
└── Procfile
```

## Getting Started

### Prerequisites

- Python 3.10+
- pip
- Git

### Installation

```bash
git clone https://github.com/eshwar698/diagnocare-backend.git
cd diagnocare-backend

python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Environment Configuration

Configure a secure JWT secret before starting the application.

**Windows PowerShell**
```powershell
$env:JWT_SECRET_KEY = "your-secure-secret"
```

**Linux / macOS**
```bash
export JWT_SECRET_KEY="your-secure-secret"
```

Never commit actual credentials or production secrets.

### Run the Backend

```bash
python app.py
```

The local development server runs at:

```text
http://127.0.0.1:5000
```

## API Modules

The backend is organized into modular route groups:

| Module | Responsibility |
|---|---|
| Authentication | User authentication and profile workflows |
| Metrics | Patient health measurements |
| Glucose Monitoring | Glucose recording and monitoring |
| Calendar | Appointment management |
| Medication | Medication reminder management |
| Reminders | Reminder workflows |
| Reports | Health report generation |
| Documents | Document upload and report processing |

Exact request payloads and response schemas are maintained in the corresponding route implementations.

## Deployment

The repository includes a Gunicorn `Procfile` for deployment.

Production deployment requires:

- Secure JWT configuration.
- A persistent database.
- Persistent file storage where uploads are retained.
- Environment-specific configuration.
- Appropriate application server configuration.

SQLite on an ephemeral hosting filesystem should not be used for persistent production health data.

## Project Status

DIAGNOCARE is an academic collaborative project and an experimental healthcare monitoring prototype.

Current limitations include:

- ML outputs are not clinically validated.
- Model performance does not establish clinical reliability.
- Predictions and explanations must not replace professional medical judgment.
- Data persistence and security requirements must be addressed before production healthcare deployment.

## Contributions

My contributions include backend development, REST API implementation, validation and error-handling improvements, integration of ML inference and explainability workflows, debugging, QA, and deployment coordination.

## Disclaimer

DIAGNOCARE is intended for educational and research purposes. It is not a medical device and must not be used to diagnose, treat, or make clinical decisions about diabetes.

---

**Repository:** [eshwar698/diagnocare-backend](https://github.com/eshwar698/diagnocare-backend)
