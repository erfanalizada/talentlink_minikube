# Monitoring Stack Testing Guide

## Prerequisites

Make sure:
- ✅ All services are running (`kubectl get pods -n talentlink-local`)
- ✅ `minikube tunnel` is running
- ✅ Hosts file has entries for grafana.local, prometheus.local, jaeger.local
- ✅ You can access http://talentlink.local

---

## Test Scenario: Create Users and Jobs, Then Query Them

We'll perform a series of operations that create observable data in all three monitoring tools.

### Step 1: Generate Write Operations (Commands)

**Task: Create 5 new user profiles**

Use these curl commands or your frontend:

```bash
# User 1
curl -X POST http://talentlink.local/api/users/profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-1",
    "username": "alice_monitor_test",
    "email": "alice@example.com",
    "role": "employee",
    "description": "Test user for monitoring",
    "phone_number": "+1234567890"
  }'

# User 2
curl -X POST http://talentlink.local/api/users/profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-2",
    "username": "bob_monitor_test",
    "email": "bob@example.com",
    "role": "employee"
  }'

# User 3
curl -X POST http://talentlink.local/api/users/profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-3",
    "username": "charlie_monitor_test",
    "email": "charlie@example.com",
    "role": "employer"
  }'

# User 4
curl -X POST http://talentlink.local/api/users/profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-4",
    "username": "diana_monitor_test",
    "email": "diana@example.com",
    "role": "employee"
  }'

# User 5
curl -X POST http://talentlink.local/api/users/profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-5",
    "username": "eve_monitor_test",
    "email": "eve@example.com",
    "role": "employer"
  }'
```

**Expected Response:** 201 Created for each

---

### Step 2: Generate Read Operations (Queries)

**Task: Query the users you just created**

```bash
# Query by ID (repeat 3 times to generate traffic)
curl http://talentlink.local/api/users/profile/test-user-1
curl http://talentlink.local/api/users/profile/test-user-1
curl http://talentlink.local/api/users/profile/test-user-1

# Query by username
curl http://talentlink.local/api/users/username/alice_monitor_test
curl http://talentlink.local/api/users/username/bob_monitor_test

# Get all profiles
curl http://talentlink.local/api/users/profiles
curl http://talentlink.local/api/users/profiles
```

**Expected Response:** 200 OK with user data

---

### Step 3: Generate Some Errors (For Testing)

**Task: Intentionally trigger errors**

```bash
# Try to get non-existent user (should return 404)
curl http://talentlink.local/api/users/profile/non-existent-user-999

# Try to create duplicate user (might return 500 or 400)
curl -X POST http://talentlink.local/api/users/profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-1",
    "username": "alice_monitor_test",
    "email": "alice@example.com",
    "role": "employee"
  }'

# Try invalid data (missing required fields)
curl -X POST http://talentlink.local/api/users/profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "invalid-user"
  }'
```

---

### Step 4: Generate Job Service Traffic

**Task: Create jobs and query them**

```bash
# Create a job
curl -X POST http://talentlink.local/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Software Engineer - Monitoring Test",
    "description": "Testing observability tools",
    "requirements": "Python, Flask, Kubernetes",
    "employer_username": "charlie_monitor_test",
    "location": "Remote",
    "salary_range": "100k-150k"
  }'

# Query jobs (repeat several times)
curl http://talentlink.local/api/jobs
curl http://talentlink.local/api/jobs
curl http://talentlink.local/api/jobs
```

---

## Now Check the Monitoring Tools!

### 🔴 Tool 1: Prometheus - View Raw Metrics

**Access:** http://prometheus.local

#### What to Do:

1. **Check Service Health**
   - Go to: Status → Targets
   - Look for: `user-service` and `job-service`
   - **Expected:** State = UP (green)

2. **Query Total Requests**
   - In the Expression box, type: `flask_http_request_total`
   - Click "Execute" → Go to "Graph" tab
   - **Expected:** See increasing line graph showing total requests

3. **Query Request Rate (Requests per second)**
   - Type: `rate(flask_http_request_total[1m])`
   - Click "Execute" → Graph
   - **Expected:** See rate of requests over time

4. **Query by Endpoint**
   - Type: `flask_http_request_total{path="/api/users/profile"}`
   - **Expected:** See count for just the profile endpoint

5. **Query Response Times**
   - Type: `flask_http_request_duration_seconds_sum`
   - **Expected:** See cumulative response time

6. **Query Error Rate**
   - Type: `flask_http_request_total{status=~"4..|5.."}`
   - **Expected:** See 404 and 500 errors from Step 3

7. **Average Response Time**
   - Type: `rate(flask_http_request_duration_seconds_sum[5m]) / rate(flask_http_request_duration_seconds_count[5m])`
   - **Expected:** Average response time in seconds

#### Screenshot Opportunities:
- Status → Targets (showing services UP)
- Graph showing request rate over time
- Table showing metrics breakdown

---

### 🟠 Tool 2: Grafana - Visualize Metrics

**Access:** http://grafana.local (admin/admin)

#### What to Do:

1. **Verify Data Source**
   - Go to: Configuration (gear icon) → Data Sources
   - Click "Prometheus"
   - Scroll down → Click "Save & Test"
   - **Expected:** "Data source is working" message

2. **Create Your First Dashboard**
   - Click "+" → Dashboard → Add new panel
   - In Query, select "Prometheus"
   - In Metrics browser, select: `flask_http_request_total`
   - **Expected:** See graph of total requests

3. **Add Request Rate Panel**
   - Click "Add panel"
   - Query: `rate(flask_http_request_total[1m])`
   - Panel title: "Request Rate (per second)"
   - Visualization: Time series
   - **Expected:** Line graph showing requests/second

4. **Add Response Time Panel**
   - Click "Add panel"
   - Query: `rate(flask_http_request_duration_seconds_sum[5m]) / rate(flask_http_request_duration_seconds_count[5m])`
   - Panel title: "Average Response Time"
   - Unit: seconds (s)
   - **Expected:** Response time graph

5. **Add Error Rate Panel**
   - Click "Add panel"
   - Query: `rate(flask_http_request_total{status=~"4..|5.."}[1m])`
   - Panel title: "Error Rate"
   - Color: Red
   - **Expected:** Spike when you ran error tests in Step 3

6. **Add Service Status Panel**
   - Click "Add panel"
   - Query: `up{job=~"user-service|job-service"}`
   - Visualization: Stat
   - Panel title: "Services Up"
   - **Expected:** Shows 1 (UP) or 0 (DOWN)

7. **Save Dashboard**
   - Click save icon (top right)
   - Name: "TalentLink CQRS Services"
   - Click "Save"

#### What You'll See:
- Real-time graphs updating
- Request spikes when you ran curl commands
- Response time variations
- Error spikes from Step 3

---

### 🔵 Tool 3: Jaeger - Trace Requests

**Access:** http://jaeger.local

#### What to Do:

1. **Select Service**
   - Service dropdown: Select "user-service"
   - Click "Find Traces"
   - **Expected:** List of recent traces

2. **Examine a Successful Request**
   - Click on a trace with 4-6 spans (successful request)
   - **Expected:** See timeline breakdown:
     ```
     ├─ GET /api/users/profile/{user_id}  [67ms total]
        ├─ handle_get_profile_by_id       [3ms]
        ├─ UserQueryHandler               [2ms]
        ├─ UserProfileService             [5ms]
        └─ SELECT FROM user_profiles      [55ms] ← Database!
     ```

3. **Analyze Database Query Time**
   - Expand the SQLAlchemy span (database query)
   - Look at "Duration"
   - **Expected:** See exact SQL query and execution time
   - **Insight:** Most time is spent in database!

4. **Compare Command vs Query**
   - Find traces for POST /api/users/profile (CreateUserProfileCommand)
   - Find traces for GET /api/users/profile/{id} (GetUserProfileByIdQuery)
   - **Expected:** POST (write) is slower than GET (read)
   - **Why:** INSERT is slower than SELECT

5. **Find the Error Trace**
   - Look for traces with red error icons
   - Click on the 404 error trace (non-existent user)
   - **Expected:** See where the error occurred in the flow
   - **Insight:** Error returned quickly (no database call for non-existent user)

6. **Examine Service Dependencies**
   - Click "System Architecture" tab
   - **Expected:** See dependency graph showing:
     - user-service → PostgreSQL
     - job-service → PostgreSQL

7. **Filter by Operation**
   - Service: "user-service"
   - Operation: Select specific endpoint like "GET /api/users/profiles"
   - **Expected:** See only traces for that operation

8. **Look at Latency Histogram**
   - Scroll down on trace list
   - **Expected:** See distribution of response times
   - **Insight:** Most requests are fast, some are slow (outliers)

#### What You'll See:
- Complete request flow visualization
- Time spent in each layer (handler, service, database)
- SQL queries executed
- Error propagation paths
- Performance bottlenecks clearly visible

---

## Interpreting Results

### What You Should Discover:

1. **From Prometheus:**
   - Total number of requests you made (~15-20)
   - Request rate spikes when you ran curl commands
   - A few errors (404, 500) from Step 3
   - Response times in milliseconds

2. **From Grafana:**
   - Visual spike in request rate when you ran tests
   - Average response time around 50-200ms
   - Error rate spike during Step 3
   - All services showing as UP

3. **From Jaeger:**
   - Database queries take most of the time (60-80% of request time)
   - Command handlers (POST) are slower than query handlers (GET)
   - Error traces show immediate failure (no DB call)
   - Each CQRS layer adds minimal overhead (<5ms)

---

## Key Insights to Note

### 📊 Metrics Show WHAT
- "We received 20 requests in the last 5 minutes"
- "Average response time is 85ms"
- "3 requests returned errors"

### 🔍 Traces Show WHERE and WHY
- "Database INSERT takes 65ms out of 85ms total"
- "GetUserProfileByIdQuery calls SELECT which takes 45ms"
- "Error occurred before reaching database (validation failure)"

### 📈 Visualization Shows TRENDS
- "Request rate is increasing"
- "Response time spikes during peak usage"
- "Error rate is acceptable (< 1%)"

---

## Advanced Tests (Optional)

### Stress Test

Generate high load to see how monitoring handles it:

```bash
# Run this in a loop (20 times)
for i in {1..20}; do
  curl http://talentlink.local/api/users/profiles &
done
wait
```

**What to observe:**
- Prometheus: Request rate spike
- Grafana: Graph shows sudden peak
- Jaeger: Many traces appear, some may be slower

### Compare Command vs Query Performance

```bash
# Create 10 users (Commands)
for i in {1..10}; do
  curl -X POST http://talentlink.local/api/users/profile \
    -H "Content-Type: application/json" \
    -d "{\"user_id\": \"perf-test-$i\", \"username\": \"user$i\", \"email\": \"user$i@test.com\", \"role\": \"employee\"}"
done

# Query 10 users (Queries)
for i in {1..10}; do
  curl http://talentlink.local/api/users/profile/perf-test-$i
done
```

**In Jaeger:**
- Filter by POST vs GET operations
- Compare average duration
- **Expected:** POST (commands) are 2-3x slower than GET (queries)

---

## Troubleshooting

### If you don't see metrics:

```bash
# Check if /metrics endpoint works
curl http://talentlink.local/api/users/metrics

# Should return Prometheus metrics format:
# flask_http_request_total{method="GET",path="/api/users/profile",status="200"} 5.0
```

### If Prometheus shows no targets:

```bash
# Check Prometheus is scraping
kubectl logs -n talentlink-local -l app=prometheus | grep -i "scrape"
```

### If traces don't appear in Jaeger:

```bash
# Check services are sending traces
kubectl logs -n talentlink-local -l app=user-service | grep -i jaeger
# Should see: "Jaeger tracing configured to jaeger:6831"
```

---

## Summary

After completing these tests, you'll have:

✅ Generated real observability data
✅ Seen metrics in Prometheus
✅ Created dashboards in Grafana
✅ Traced requests through your CQRS architecture in Jaeger
✅ Understood where time is spent in your application
✅ Identified that database queries are the main bottleneck
✅ Compared command (write) vs query (read) performance

**Next Steps:**
- Set up alerts in Grafana for high error rates
- Create custom dashboards for business metrics
- Use Jaeger to optimize slow database queries
- Implement caching for frequently-queried data
