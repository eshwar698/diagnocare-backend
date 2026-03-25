from config import create_app, db
import models
from routes.profile_routes import profile_bp
from routes.auth_routes import auth_bp
from routes.metric_routes import metric_bp
from routes.calender_routes import calendar_bp
from routes.medicine_routes import medicine_bp
from routes.reminder_routes import reminder_bp
from routes.report_routes import report_bp
from services.model_loader import load_model
from routes.glucose_monitor_routes import glucose_monitor_bp
from routes.document_routes import document_bp
from flask_cors import CORS
app = create_app()
CORS(app, supports_credentials=True)
# Register blueprints with prefixes

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(metric_bp, url_prefix="/metrics")
app.register_blueprint(calendar_bp, url_prefix="/calendar")
app.register_blueprint(medicine_bp, url_prefix="/medicine")
app.register_blueprint(reminder_bp, url_prefix="/reminders")   # NEW BLUEPRINT
app.register_blueprint(report_bp, url_prefix="/reports")
app.register_blueprint(profile_bp, url_prefix="/auth")
app.register_blueprint(glucose_monitor_bp, url_prefix="/glucose-monitor")
app.register_blueprint(document_bp, url_prefix="/document")

import os

os.makedirs("uploads",exist_ok=True)
os.makedirs("instance",exist_ok=True)

if __name__ == "__main__":

    with app.app_context():
        db.create_all()
    load_model()
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)