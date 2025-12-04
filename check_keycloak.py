import requests
import json

# Get admin token
token_response = requests.post(
    "http://localhost:8080/realms/master/protocol/openid-connect/token",
    data={
        "username": "admin",
        "password": "admin",
        "grant_type": "password",
        "client_id": "admin-cli"
    }
)

if token_response.status_code != 200:
    print(f"Failed to get token: {token_response.text}")
    exit(1)

token = token_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# List all realms
print("=" * 50)
print("REALMS:")
print("=" * 50)
realms_response = requests.get("http://localhost:8080/admin/realms", headers=headers)
realms = realms_response.json()
for realm in realms:
    print(f"  - {realm['realm']}")

# Check for talentlink realm (case-insensitive)
talentlink_realm = None
for realm in realms:
    if realm['realm'].lower() == 'talentlink':
        talentlink_realm = realm['realm']
        break

if not talentlink_realm:
    print("\n❌ No 'talentlink' realm found!")
    exit(1)

print(f"\n✅ Found realm: {talentlink_realm}")

# List clients in the talentlink realm
print("\n" + "=" * 50)
print(f"CLIENTS in {talentlink_realm} realm:")
print("=" * 50)
clients_response = requests.get(
    f"http://localhost:8080/admin/realms/{talentlink_realm}/clients",
    headers=headers
)
clients = clients_response.json()

for client in clients:
    client_id = client.get('clientId', 'N/A')
    enabled = client.get('enabled', False)
    public = client.get('publicClient', False)
    direct_access_grants = client.get('directAccessGrantsEnabled', False)

    print(f"\n  Client ID: {client_id}")
    print(f"    - Enabled: {enabled}")
    print(f"    - Public: {public}")
    print(f"    - Direct Access Grants (password flow): {direct_access_grants}")

    # Check for talentlink-backend client
    if client_id == 'talentlink-backend':
        print(f"    - ⭐ This is our target client!")
        print(f"    - UUID: {client['id']}")

        # Get client secret
        secret_response = requests.get(
            f"http://localhost:8080/admin/realms/{talentlink_realm}/clients/{client['id']}/client-secret",
            headers=headers
        )
        if secret_response.status_code == 200:
            secret_data = secret_response.json()
            print(f"    - Secret: {secret_data.get('value', 'N/A')}")
        else:
            print(f"    - Secret: Could not retrieve (status {secret_response.status_code})")
