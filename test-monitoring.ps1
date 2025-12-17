# TalentLink Monitoring System Quick Test
# This script demonstrates that your monitoring system is working

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   TalentLink Monitoring System Test" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Verify Monitoring Pods
Write-Host "[Test 1] Checking Monitoring Pods Status..." -ForegroundColor Yellow
kubectl get pods -n talentlink-local | Select-String -Pattern "prometheus|grafana|jaeger|elasticsearch|redis"

Start-Sleep -Seconds 2

# Test 2: Port Forward Services
Write-Host "`n[Test 2] Setting up Port Forwarding..." -ForegroundColor Yellow
Write-Host "Starting port forwards (these will run in background)..." -ForegroundColor Gray

# Kill any existing port forwards
Get-Process -Name kubectl -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*port-forward*"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Port forward monitoring services
Start-Process -NoNewWindow kubectl -ArgumentList "port-forward -n talentlink-local svc/prometheus 9090:9090"
Start-Process -NoNewWindow kubectl -ArgumentList "port-forward -n talentlink-local svc/grafana 3000:3000"
Start-Process -NoNewWindow kubectl -ArgumentList "port-forward -n talentlink-local svc/jaeger 16686:16686"
Start-Process -NoNewWindow kubectl -ArgumentList "port-forward -n talentlink-local svc/job-service 5000:5000"

Write-Host "Waiting for port forwards to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Test 3: Check Prometheus Targets
Write-Host "`n[Test 3] Checking Prometheus Status..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:9090/-/healthy" -TimeoutSec 5
    Write-Host "✅ Prometheus is healthy" -ForegroundColor Green
} catch {
    Write-Host "❌ Prometheus is not responding" -ForegroundColor Red
}

# Test 4: Check Grafana
Write-Host "`n[Test 4] Checking Grafana Status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -TimeoutSec 5
    Write-Host "✅ Grafana is healthy" -ForegroundColor Green
} catch {
    Write-Host "❌ Grafana is not responding" -ForegroundColor Red
}

# Test 5: Check Jaeger
Write-Host "`n[Test 5] Checking Jaeger Status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:16686/" -TimeoutSec 5
    Write-Host "✅ Jaeger is accessible" -ForegroundColor Green
} catch {
    Write-Host "❌ Jaeger is not responding" -ForegroundColor Red
}

# Test 6: Generate Load and Metrics
Write-Host "`n[Test 6] Generating Load to Create Metrics..." -ForegroundColor Yellow
Write-Host "Making 20 API calls to job-service..." -ForegroundColor Gray

$jobs = @()
for ($i = 1; $i -le 20; $i++) {
    $jobs += Start-Job -ScriptBlock {
        param($url)
        try {
            Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 5 | Out-Null
        } catch {
            # Ignore errors
        }
    } -ArgumentList "http://localhost:5000/health"
}

# Wait for all jobs to complete
$jobs | Wait-Job | Out-Null
$jobs | Remove-Job

Write-Host "✅ Load generation completed" -ForegroundColor Green

# Test 7: Check Redis Cache
Write-Host "`n[Test 7] Testing Redis Cache..." -ForegroundColor Yellow
kubectl exec -n talentlink-local deployment/redis -- redis-cli ping

$keys = kubectl exec -n talentlink-local deployment/redis -- redis-cli KEYS "*"
Write-Host "Cache keys found: $($keys.Count)" -ForegroundColor Cyan

# Test 8: Check HPA Status
Write-Host "`n[Test 8] Checking Horizontal Pod Autoscaler..." -ForegroundColor Yellow
kubectl get hpa -n talentlink-local

# Test 9: Query Prometheus Metrics
Write-Host "`n[Test 9] Querying Prometheus Metrics..." -ForegroundColor Yellow
try {
    $query = "up{namespace='talentlink-local'}"
    $prometheusUrl = "http://localhost:9090/api/v1/query?query=$([uri]::EscapeDataString($query))"
    $response = Invoke-RestMethod -Uri $prometheusUrl -TimeoutSec 5

    if ($response.status -eq "success") {
        Write-Host "✅ Prometheus metrics query successful" -ForegroundColor Green
        Write-Host "Active targets: $($response.data.result.Count)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Failed to query Prometheus metrics" -ForegroundColor Red
}

# Test 10: Check Node Resources
Write-Host "`n[Test 10] Checking Node Resource Usage..." -ForegroundColor Yellow
kubectl top nodes

# Summary and Next Steps
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   Test Summary" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Access your monitoring tools at:" -ForegroundColor Yellow
Write-Host "  📊 Prometheus: " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:9090" -ForegroundColor Green
Write-Host "  📈 Grafana:    " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:3000" -ForegroundColor Green -NoNewline
Write-Host " (admin/admin)" -ForegroundColor DarkGray
Write-Host "  🔍 Jaeger:     " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:16686" -ForegroundColor Green

Write-Host "`nRecommended Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open Prometheus and check Status → Targets" -ForegroundColor Gray
Write-Host "  2. Open Grafana and add Prometheus data source" -ForegroundColor Gray
Write-Host "  3. Open Jaeger and search for 'job-service' traces" -ForegroundColor Gray
Write-Host "  4. Review the detailed test plan in:" -ForegroundColor Gray
Write-Host "     docs/monitoring_test_plan.md`n" -ForegroundColor Cyan

Write-Host "To stop port forwarding, run:" -ForegroundColor Yellow
Write-Host "  Get-Process kubectl | Where-Object {`$_.CommandLine -like '*port-forward*'} | Stop-Process`n" -ForegroundColor Gray
