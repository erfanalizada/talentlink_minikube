import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from keycloak import KeycloakOpenID, KeycloakAdmin
from dotenv import load_dotenv
from prometheus_flask_exporter import PrometheusMetrics
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource

load_dotenv()
app = Flask(__name__)
CORS(app,
     resources={r"/api/*": {
         "origins": "*",
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"]
     }},
     supports_credentials=True)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)
metrics.info('auth_service_info', 'Auth Service with Keycloak', version='1.0.0')

# Initialize Jaeger tracing
jaeger_host = os.getenv('JAEGER_HOST', 'jaeger')
jaeger_port = int(os.getenv('JAEGER_PORT', '6831'))

resource = Resource.create({"service.name": "auth-service"})
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

print("✅ Auth service initialized successfully")
print(f"📊 Prometheus metrics available at /metrics")
print(f"🔍 Jaeger tracing configured to {jaeger_host}:{jaeger_port}")

# ---------------- KEYCLOAK CONFIG ----------------
KC_URL = os.getenv("KEYCLOAK_URL")  # IMPORTANT: no slash here
REALM = os.getenv("KEYCLOAK_REALM")
PUB_ID = os.getenv("KEYCLOAK_PUBLIC_CLIENT_ID")
CONF_ID = os.getenv("KEYCLOAK_CONFIDENTIAL_CLIENT_ID")
CONF_SEC = os.getenv("KEYCLOAK_CONFIDENTIAL_SECRET")
ADMIN = os.getenv("KEYCLOAK_ADMIN_USER")
ADMIN_PW = os.getenv("KEYCLOAK_ADMIN_PASS")

# ----------- OpenID client (password grant) -----------
oidc = KeycloakOpenID(
    server_url=KC_URL,       # http://keycloak.local
    realm_name=REALM,
    client_id=CONF_ID,
    client_secret_key=CONF_SEC
)

# --------------- Admin API client -------------------
admin = KeycloakAdmin(
    server_url=KC_URL,       # http://keycloak.local
    username=ADMIN,
    password=ADMIN_PW,
    realm_name=REALM,
    user_realm_name="master",
    verify=False            # important for local HTTP ingress
)

def _get_role(role_name):
    roles = admin.get_realm_roles()
    for r in roles:
        if r["name"] == role_name:
            return r
    raise ValueError(f"Role '{role_name}' not found")


# ---------------- ROUTES ----------------

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    print(f"📝 Register request received: username={username}, email={email}, role={role}")

    if not all([username, email, password, role]):
        print(f"❌ Missing fields: username={bool(username)}, email={bool(email)}, password={bool(password)}, role={bool(role)}")
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Create user
        print(f"🔄 Creating user in Keycloak: {username}")
        user_id = admin.create_user({
            "username": username,
            "email": email,
            "emailVerified": True,
            "enabled": True,
        })

        print(f"🔑 Setting password for user: {user_id}")
        admin.set_user_password(user_id=user_id, password=password, temporary=False)

        # Assign role
        print(f"👤 Assigning role '{role}' to user")
        kc_role = _get_role(role)
        admin.assign_realm_roles(user_id=user_id, roles=[kc_role])

        # Create user profile in user-service
        print(f"📋 Creating user profile in user-service for user_id: {user_id}")
        try:
            user_service_url = os.getenv("USER_SERVICE_URL", "http://user-service:5000")
            profile_response = requests.post(
                f"{user_service_url}/api/users/profile",
                json={
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "role": role,
                    "description": data.get("description"),
                    "phone_number": data.get("phone_number"),
                    "secondary_email": data.get("secondary_email"),
                    "address": data.get("address")
                },
                timeout=5
            )

            if profile_response.status_code == 201:
                print(f"✅ User profile created successfully")
            else:
                print(f"⚠️ Warning: User profile creation failed with status {profile_response.status_code}")
                print(f"Response: {profile_response.text}")
        except Exception as profile_error:
            print(f"⚠️ Warning: Could not create user profile: {str(profile_error)}")
            # Don't fail registration if profile creation fails
            pass

        print(f"✅ User '{username}' created successfully with ID: {user_id}")
        return jsonify({"message": f"User '{username}' created", "id": user_id}), 201

    except Exception as e:
        import traceback
        print(f"❌ Registration error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 400


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username & password required"}), 400

    try:
        token = oidc.token(username, password, grant_type="password")
        return jsonify({
            "access_token": token["access_token"],
            "refresh_token": token["refresh_token"],
            "expires_in": token["expires_in"],
        })

    except Exception as e:
        import traceback
        print("⚠️ Keycloak login error:")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 401


@app.route("/api/auth/health")
def health():
    return jsonify({"status": "auth-service ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
