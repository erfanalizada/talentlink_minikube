"""
Main Flask application.
Single Responsibility: Application setup and configuration.
Dependency Inversion: Uses dependency injection for components.
"""
import os
from flask import Flask
from flask_cors import CORS
from database import init_db
from routes import user_bp
from prometheus_flask_exporter import PrometheusMetrics
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource


def create_app():
    """
    Application factory pattern.
    Open/Closed: Can extend with new configurations without modifying core logic.
    """
    app = Flask(__name__)

    # CORS configuration
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Initialize Prometheus metrics
    metrics = PrometheusMetrics(app)
    metrics.info('user_service_info', 'User Service with CQRS', version='1.0.0')

    # Initialize Jaeger tracing
    jaeger_host = os.getenv('JAEGER_HOST', 'jaeger')
    jaeger_port = int(os.getenv('JAEGER_PORT', '6831'))

    resource = Resource.create({"service.name": "user-service"})
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
    app.register_blueprint(user_bp)

    # Initialize database
    with app.app_context():
        try:
            init_db()
            # Instrument SQLAlchemy after database initialization
            SQLAlchemyInstrumentor().instrument()
        except Exception as e:
            print(f"⚠️ Database initialization warning: {e}")

    print("✅ User service initialized successfully")
    print(f"📊 Prometheus metrics available at /metrics")
    print(f"🔍 Jaeger tracing configured to {jaeger_host}:{jaeger_port}")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
