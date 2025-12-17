#!/bin/bash

# TalentLink Monitoring System Quick Test
# This script demonstrates that your monitoring system is working

CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

echo -e "\n${CYAN}========================================"
echo -e "   TalentLink Monitoring System Test"
echo -e "========================================${NC}\n"

# Test 1: Verify Monitoring Pods
echo -e "${YELLOW}[Test 1] Checking Monitoring Pods Status...${NC}"
kubectl get pods -n talentlink-local | grep -E "prometheus|grafana|jaeger|elasticsearch|redis"

sleep 2

# Test 2: Port Forward Services
echo -e "\n${YELLOW}[Test 2] Setting up Port Forwarding...${NC}"
echo -e "${GRAY}Starting port forwards (these will run in background)...${NC}"

# Kill any existing port forwards
pkill -f "kubectl port-forward" 2>/dev/null

# Port forward monitoring services
kubectl port-forward -n talentlink-local svc/prometheus 9090:9090 &>/dev/null &
kubectl port-forward -n talentlink-local svc/grafana 3000:3000 &>/dev/null &
kubectl port-forward -n talentlink-local svc/jaeger 16686:16686 &>/dev/null &
kubectl port-forward -n talentlink-local svc/job-service 5000:5000 &>/dev/null &

echo -e "${GRAY}Waiting for port forwards to initialize...${NC}"
sleep 5

# Test 3: Check Prometheus Targets
echo -e "\n${YELLOW}[Test 3] Checking Prometheus Status...${NC}"
if curl -s -f http://localhost:9090/-/healthy &>/dev/null; then
    echo -e "${GREEN}✅ Prometheus is healthy${NC}"
else
    echo -e "${RED}❌ Prometheus is not responding${NC}"
fi

# Test 4: Check Grafana
echo -e "\n${YELLOW}[Test 4] Checking Grafana Status...${NC}"
if curl -s -f http://localhost:3000/api/health &>/dev/null; then
    echo -e "${GREEN}✅ Grafana is healthy${NC}"
else
    echo -e "${RED}❌ Grafana is not responding${NC}"
fi

# Test 5: Check Jaeger
echo -e "\n${YELLOW}[Test 5] Checking Jaeger Status...${NC}"
if curl -s -f http://localhost:16686/ &>/dev/null; then
    echo -e "${GREEN}✅ Jaeger is accessible${NC}"
else
    echo -e "${RED}❌ Jaeger is not responding${NC}"
fi

# Test 6: Generate Load and Metrics
echo -e "\n${YELLOW}[Test 6] Generating Load to Create Metrics...${NC}"
echo -e "${GRAY}Making 50 API calls to job-service...${NC}"

for i in {1..50}; do
    curl -s http://localhost:5000/health &>/dev/null &
    if [ $((i % 10)) -eq 0 ]; then
        wait
    fi
done
wait

echo -e "${GREEN}✅ Load generation completed${NC}"

# Test 7: Check Redis Cache
echo -e "\n${YELLOW}[Test 7] Testing Redis Cache...${NC}"
kubectl exec -n talentlink-local deployment/redis -- redis-cli ping

KEY_COUNT=$(kubectl exec -n talentlink-local deployment/redis -- redis-cli KEYS "*" 2>/dev/null | wc -l)
echo -e "${CYAN}Cache keys found: $KEY_COUNT${NC}"

# Test 8: Check HPA Status
echo -e "\n${YELLOW}[Test 8] Checking Horizontal Pod Autoscaler...${NC}"
kubectl get hpa -n talentlink-local

# Test 9: Query Prometheus Metrics
echo -e "\n${YELLOW}[Test 9] Querying Prometheus Metrics...${NC}"
RESPONSE=$(curl -s "http://localhost:9090/api/v1/query?query=up{namespace='talentlink-local'}")

if echo "$RESPONSE" | grep -q '"status":"success"'; then
    echo -e "${GREEN}✅ Prometheus metrics query successful${NC}"
    TARGET_COUNT=$(echo "$RESPONSE" | grep -o '"metric"' | wc -l)
    echo -e "${CYAN}Active targets: $TARGET_COUNT${NC}"
else
    echo -e "${RED}❌ Failed to query Prometheus metrics${NC}"
fi

# Test 10: Check Node Resources
echo -e "\n${YELLOW}[Test 10] Checking Node Resource Usage...${NC}"
kubectl top nodes 2>/dev/null || echo "Metrics server not available"

# Summary and Next Steps
echo -e "\n${CYAN}========================================"
echo -e "   Test Summary"
echo -e "========================================${NC}\n"

echo -e "${YELLOW}Access your monitoring tools at:${NC}"
echo -e "  ${GRAY}📊 Prometheus:${NC} ${GREEN}http://localhost:9090${NC}"
echo -e "  ${GRAY}📈 Grafana:   ${NC} ${GREEN}http://localhost:3000${NC} ${GRAY}(admin/admin)${NC}"
echo -e "  ${GRAY}🔍 Jaeger:    ${NC} ${GREEN}http://localhost:16686${NC}"

echo -e "\n${YELLOW}Recommended Next Steps:${NC}"
echo -e "  ${GRAY}1. Open Prometheus and check Status → Targets${NC}"
echo -e "  ${GRAY}2. Open Grafana and add Prometheus data source${NC}"
echo -e "  ${GRAY}3. Open Jaeger and search for 'job-service' traces${NC}"
echo -e "  ${GRAY}4. Review the detailed test plan in:${NC}"
echo -e "     ${CYAN}docs/monitoring_test_plan.md${NC}\n"

echo -e "${YELLOW}To stop port forwarding, run:${NC}"
echo -e "  ${GRAY}pkill -f 'kubectl port-forward'${NC}\n"
