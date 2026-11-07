# DIAGNOCARE — Diabetes Risk Monitoring Backend

> A backend service for monitoring risk trends in people already diagnosed with diabetes. DIAGNOCARE is a monitoring and decision-support prototype—not a diagnostic tool or a diabetes-prediction system.

## Overview

DIAGNOCARE brings patient-record management, glucose tracking, medication and reminder workflows, reporting, and ML-assisted risk monitoring behind a Flask REST API. The backend connects application data and a temporal XGBoost model, with SHAP-based explanations intended to make model outputs more interpretable.

## Capabilities

- **Authentication & profiles:** JWT-based authentication and profile endpoints.
- **Health metrics:** recording and retrieving patient metrics, including glucose-related measurements.
- **Glucose monitoring:** monitoring workflows and trend-related services.
- **Medication & reminders:** medication management and reminder endpoints/services.
- **Reports & documents:** report generation and document-related routes.
- **Risk monitoring:** feature engineering and inference using a temporal XGBoost model; explanation support through SHAP.
- **API organization:** Flask Blueprints separate route groups from service logic.

> Exact endpoint payloads and behavior are defined in the source under `routes/` and `services/`. This README intentionally avoids inventing endpoint contracts.

## Architecture

```text
Client application (Flutter)
        │  HTTP / REST
        ▼
Flask application (app.py)
        ├── Auth & profile routes
        ├── Metrics & glucose-monitor routes
        ├── Calendar, medicine & reminder routes
        ├── Reports & document routes
        └── Services
             ├── Feature engineering
             ├── ML inference / model loader
             ├── Trends & insights
             └── Reports / reminders
        │
        ├── SQLAlchemy ── SQLite (local default)
        └── Temporal XGBoost model + feature metadata
```

## Technology stack

- **Language:** Python
- **API:** Flask, Flask-RESTful, Flask Blueprints, Flask-CORS
- **Persistence:** SQLAlchemy, Flask-SQLAlchemy, SQLite (default local configuration)
- **Authentication:** Flask-JWT-Extended
- **ML / data:** pandas, NumPy, scikit-learn, XGBoost, SHAP, joblib
- **Deployment:** Gunicorn; deployment configuration via `Procfile`

## Repository layout

```text
.
├── app.py                  # Flask app and Blueprint registration
├── config.py               # Application/database/JWT configuration
├── models.py                # SQLAlchemy data models
├── predict_temporal.py      # Temporal inference utilities
├── routes/                  # API route Blueprints
├── services/                # Business logic and ML/report services
├── utils/                   # Shared utilities and validators
├── temporal_xgb_model.pkl   # Active trained model artifact
├── label_encoder.pkl        # Label encoder artifact
├── feature_columns.pkl      # Model feature-column metadata
├── requirements.txt
└── Procfile
```

## Local setup

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/eshwar698/diagnocare-backend.git
cd diagnocare-backend
python -m venv .venv
```

Activate it:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure environment variables

Set a unique secret before running the app. Do not commit real secrets.

```powershell
# Windows PowerShell (current terminal)
$env:JWT_SECRET_KEY = "replace-with-a-long-random-secret"
```

```bash
# macOS / Linux
export JWT_SECRET_KEY="replace-with-a-long-random-secret"
```

The current local configuration uses SQLite by default. Database tables are created by the application entry point when run directly.

### 4. Run locally

```bash
python app.py
```

The development server listens on `http://127.0.0.1:5000` by default (or the port supplied through `PORT`). Do not use Flask's development server for production deployment.

## Deployment

The repository includes a `Procfile` for Gunicorn-based hosting. Configure the platform with:

- `JWT_SECRET_KEY`: a strong, unique secret value.
- `PORT`: supplied by the hosting platform where applicable.
- A persistent database and storage strategy appropriate to the deployment environment.

**Important:** SQLite on an ephemeral host filesystem is not suitable for durable production data. Use a managed/persistent database for production and configure the application accordingly.

## Model artifacts

The backend currently loads these artifacts through `services/model_loader.py`:

- `temporal_xgb_model.pkl`
- `label_encoder.pkl`
- `feature_columns.pkl`

Keep these files version-compatible with the model code and feature-generation logic. Pickle/joblib artifacts should only be loaded from trusted sources.

## Project status & limitations

- This is an academic/collaborative software project and a prototype for diabetes risk monitoring.
- Model outputs are experimental decision-support signals and must not be interpreted as medical diagnoses or treatment recommendations.
- Model performance depends on the training data, feature construction, and deployment context; it does not establish clinical validity.
- The repository contains the backend. The Flutter client and research materials may be maintained separately.
- The research paper associated with the project is **not published or accepted**; do not treat it as a publication.

## Contributions

My contribution focused on backend development, API integration, ML pipeline integration, debugging, and deployment coordination within the collaborative project. I also initiated preparation of a research manuscript; its publication status remains unpublished.

## License

No license is currently specified. Unless a license is added, the repository is not automatically open for reuse, redistribution, or modification by others.
