 1. Services Up/Down
  up{job=~".*-service"}

  2. Service Availability by Job
  avg_over_time(up{job=~".*-service"}[5m])

  3. Services Health Status (by kubernetes namespace)
  up{kubernetes_namespace="talentlink-local"}

  ---
  HTTP Request Metrics

  4. Request Rate (requests/second) - All Services
  rate(flask_http_request_duration_seconds_count[5m])

  5. Request Rate by Path
  sum(rate(flask_http_request_duration_seconds_count[5m])) by (path)

  6. Request Rate by Service and Method
  sum(rate(flask_http_request_duration_seconds_count{kubernetes_namespace="talentlink-local"}[5m])) by (app, method)

  7. Request Rate by Status Code
  sum(rate(flask_http_request_duration_seconds_count[5m])) by (status)

  8. HTTP Error Rate (4xx and 5xx)
  sum(rate(flask_http_request_duration_seconds_count{status=~"4..|5.."}[5m]))

  9. Success Rate Percentage
  sum(rate(flask_http_request_duration_seconds_count{status=~"2.."}[5m])) 
  / 
  sum(rate(flask_http_request_duration_seconds_count[5m])) * 100

  ---
  Latency & Performance

  10. Average Request Duration (all services)
  rate(flask_http_request_duration_seconds_sum[5m]) 
  / 
  rate(flask_http_request_duration_seconds_count[5m])

  11. 95th Percentile Latency
  histogram_quantile(0.95, rate(flask_http_request_duration_seconds_bucket[5m]))

  12. 99th Percentile Latency
  histogram_quantile(0.99, rate(flask_http_request_duration_seconds_bucket[5m]))

  13. Median Latency (50th percentile)
  histogram_quantile(0.50, rate(flask_http_request_duration_seconds_bucket[5m]))

  14. Latency by Endpoint
  histogram_quantile(0.95, sum(rate(flask_http_request_duration_seconds_bucket[5m])) by (path, le))

  15. Slowest Endpoints (Top 5)
  topk(5,
    rate(flask_http_request_duration_seconds_sum[5m]) 
    / 
    rate(flask_http_request_duration_seconds_count[5m])
  )

  ---
  Auth Service Specific

  16. Login Requests per Second
  rate(flask_http_request_duration_seconds_count{path="/api/auth/login"}[5m])

  17. Registration Requests per Second
  rate(flask_http_request_duration_seconds_count{path="/api/auth/register"}[5m])

  18. Failed Login Attempts (401 errors)
  rate(flask_http_request_duration_seconds_count{path="/api/auth/login", status="401"}[5m])

  19. Auth Service Health Check Rate
  rate(flask_http_request_duration_seconds_count{path="/api/auth/health"}[5m])

  ---
  Resource Usage (Process Level)

  20. Memory Usage by Service (MB)
  process_resident_memory_bytes / 1024 / 1024

  21. CPU Seconds Total
  rate(process_cpu_seconds_total[5m])

  22. Open File Descriptors
  process_open_fds

  ---
  Python Garbage Collection

  23. Python GC Collections
  rate(python_gc_collections_total[5m])

  24. Python GC Objects Collected
  rate(python_gc_objects_collected_total[5m])

  ---
  Top N Queries

  25. Top 5 Most Active Endpoints
  topk(5, sum(rate(flask_http_request_duration_seconds_count[5m])) by (path))

  26. Top Services by Request Volume
  topk(5, sum(rate(flask_http_request_duration_seconds_count{kubernetes_namespace="talentlink-local"}[5m])) by (app))

  27. Endpoints with Most Errors
  topk(5, sum(rate(flask_http_request_duration_seconds_count{status=~"5.."}[5m])) by (path))

  ---
  Service Comparison

  28. Request Rate Comparison Across Services
  sum(rate(flask_http_request_duration_seconds_count{kubernetes_namespace="talentlink-local"}[5m])) by (app)

  29. Latency Comparison Across Services
  avg(rate(flask_http_request_duration_seconds_sum{kubernetes_namespace="talentlink-local"}[5m])
  /
  rate(flask_http_request_duration_seconds_count{kubernetes_namespace="talentlink-local"}[5m])) by (app)

  30. Error Rate by Service
  sum(rate(flask_http_request_duration_seconds_count{status=~"5..", kubernetes_namespace="talentlink-local"}[5m])) by (app)
