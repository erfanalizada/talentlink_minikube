"""
Job Service - Main application entry point.
Handles job postings and applications.
"""
import os
from flask import Flask
from flask_cors import CORS
from database import init_db
from routes import jobs_bp
from prometheus_flask_exporter import PrometheusMetrics
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource

app = Flask(__name__)
# Enable CORS for frontend communication. Explicitly allow the frontend origin
# and the cluster host so Access-Control-Allow-Credentials can be used safely.
CORS(app,
    resources={r"/api/*": {"origins": ["http://localhost:3000", "http://talentlink.local"]}},
    supports_credentials=True)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)
metrics.info('job_service_info', 'Job Service with CQRS', version='1.0.0')

# Initialize Jaeger tracing
jaeger_host = os.getenv('JAEGER_HOST', 'jaeger')
jaeger_port = int(os.getenv('JAEGER_PORT', '6831'))

resource = Resource.create({"service.name": "job-service"})
trace.set_tracer_provider(TracerProvider(resource=resource))

jaeger_exporter = JaegerExporter(
    agent_host_name=jaeger_host,
    agent_port=jaeger_port,
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Instrument Flask app
FlaskInstrumentor().instrument_app(app)

# Register blueprints
app.register_blueprint(jobs_bp)

# Initialize database on startup
with app.app_context():
    init_db()
    # Instrument SQLAlchemy after database initialization
    SQLAlchemyInstrumentor().instrument()

print("✅ Job service initialized successfully")
print(f"📊 Prometheus metrics available at /metrics")
print(f"🔍 Jaeger tracing configured to {jaeger_host}:{jaeger_port}")

# Note: app is already created at module level above

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
