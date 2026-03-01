#!/bin/bash
# Quick Validation Test Script for AI Legal Research Assistant
# Usage: bash scripts/test_quick.sh

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"
PASS_COUNT=0
TOTAL_TESTS=6

echo -e "${CYAN}"
echo "============================================"
echo "🧪 AI Legal Assistant - Quick Validation"
echo "============================================"
echo -e "${NC}"

# Test 1: Health Check
echo -e "${YELLOW}[1/6] Testing API Health Check...${NC}"
health_response=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
http_code=$(echo "$health_response" | tail -n1)
health_body=$(echo "$health_response" | sed '$d')

if [ "$http_code" = "200" ]; then
    status=$(echo "$health_body" | grep -o '"status":"[^"]*' | cut -d'"' -f4)
    if [ "$status" = "healthy" ]; then
        echo -e "  ${GREEN}✅ PASS: API is healthy${NC}"
        docs_indexed=$(echo "$health_body" | grep -o '"documents_indexed":[0-9]*' | cut -d':' -f2)
        echo -e "  ${GRAY}📊 Status: healthy${NC}"
        echo -e "  ${GRAY}📦 Documents Indexed: $docs_indexed${NC}"
        ((PASS_COUNT++))
    else
        echo -e "  ${RED}❌ FAIL: API returned unhealthy status${NC}"
    fi
else
    echo -e "  ${RED}❌ FAIL: Cannot connect to API at $BASE_URL${NC}"
    echo -e "  ${YELLOW}💡 Make sure the server is running: python -m app.main${NC}"
fi

sleep 0.5

# Test 2: API Documentation
echo -e "\n${YELLOW}[2/6] Testing API Documentation...${NC}"
docs_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs")
if [ "$docs_code" = "200" ]; then
    echo -e "  ${GREEN}✅ PASS: Swagger documentation accessible${NC}"
    echo -e "  ${GRAY}🔗 URL: $BASE_URL/docs${NC}"
    ((PASS_COUNT++))
else
    echo -e "  ${RED}❌ FAIL: Documentation not accessible${NC}"
fi

sleep 0.5

# Test 3: Document Upload
echo -e "\n${YELLOW}[3/6] Testing Document Upload...${NC}"
test_content="SUPREME COURT TEST CASE

Case Number: TEST-2024-001
Court: Test District Court

FACTS:
This is a test legal document about contract law. The case involves a breach of contract claim 
where the defendant failed to deliver goods within the specified timeframe. The contract included 
a 'time is of the essence' clause, making timely delivery critical.

ISSUE:
Whether the delay constitutes a material breach of contract.

HOLDING:
The court held that the delay was a material breach due to the time-sensitive nature of the contract.

REASONING:
Courts strictly enforce contracts with 'time is of the essence' clauses. The defendant's failure 
to meet the deadline caused measurable damages to the plaintiff's business operations.

CONCLUSION:
Judgment for the plaintiff. Defendant liable for breach of contract damages."

upload_response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/documents/upload" \
  -H "Content-Type: application/json" \
  -d "{
    \"filename\": \"test_contract_case.txt\",
    \"content\": \"$(echo "$test_content" | sed 's/"/\\"/g' | tr '\n' ' ')\",
    \"metadata\": {
      \"case_number\": \"TEST-2024-001\",
      \"court\": \"Test District Court\",
      \"topic\": \"Contract Law\",
      \"test_document\": true
    }
  }")

upload_code=$(echo "$upload_response" | tail -n1)
upload_body=$(echo "$upload_response" | sed '$d')

if [ "$upload_code" = "200" ]; then
    echo -e "  ${GREEN}✅ PASS: Document uploaded successfully${NC}"
    doc_id=$(echo "$upload_body" | grep -o '"doc_id":"[^"]*' | cut -d'"' -f4)
    num_chunks=$(echo "$upload_body" | grep -o '"num_chunks":[0-9]*' | cut -d':' -f2)
    size_bytes=$(echo "$upload_body" | grep -o '"size_bytes":[0-9]*' | cut -d':' -f2)
    echo -e "  ${GRAY}📄 Document ID: $doc_id${NC}"
    echo -e "  ${GRAY}📊 Chunks Created: $num_chunks${NC}"
    echo -e "  ${GRAY}💾 Size: $size_bytes bytes${NC}"
    ((PASS_COUNT++))
else
    echo -e "  ${RED}❌ FAIL: Document upload failed${NC}"
    echo -e "  ${YELLOW}💡 Response code: $upload_code${NC}"
fi

sleep 2  # Give time for indexing

# Test 4: List Documents
echo -e "\n${YELLOW}[4/6] Testing Document Listing...${NC}"
docs_response=$(curl -s -w "\n%{http_code}" "$BASE_URL/documents")
docs_code=$(echo "$docs_response" | tail -n1)
docs_body=$(echo "$docs_response" | sed '$d')

if [ "$docs_code" = "200" ]; then
    doc_count=$(echo "$docs_body" | grep -o '"' | wc -l)
    if [ "$doc_count" -gt 2 ]; then
        echo -e "  ${GREEN}✅ PASS: Documents retrieved successfully${NC}"
        echo -e "  ${GRAY}📚 Documents found in database${NC}"
        ((PASS_COUNT++))
    else
        echo -e "  ${YELLOW}⚠️  WARN: No documents found (this might be expected)${NC}"
    fi
else
    echo -e "  ${RED}❌ FAIL: Cannot retrieve document list${NC}"
fi

sleep 0.5

# Test 5: Semantic Search
echo -e "\n${YELLOW}[5/6] Testing Semantic Search...${NC}"
start_time=$(date +%s%3N)
search_response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What constitutes a material breach of contract when time is of the essence?",
    "top_k": 3,
    "include_citations": true
  }')
end_time=$(date +%s%3N)
duration=$((end_time - start_time))

search_code=$(echo "$search_response" | tail -n1)
search_body=$(echo "$search_response" | sed '$d')

if [ "$search_code" = "200" ]; then
    echo -e "  ${GREEN}✅ PASS: Search completed successfully${NC}"
    echo -e "  ${GRAY}⏱️  Search Time: ${duration}ms${NC}"
    
    model_used=$(echo "$search_body" | grep -o '"model_used":"[^"]*' | cut -d'"' -f4)
    echo -e "  ${GRAY}🤖 Model Used: $model_used${NC}"
    
    # Extract answer preview (first 100 chars)
    answer=$(echo "$search_body" | grep -o '"answer":"[^"]*' | cut -d'"' -f4 | head -c 100)
    echo -e "  ${GRAY}💡 Answer Preview: $answer...${NC}"
    
    ((PASS_COUNT++))
else
    echo -e "  ${RED}❌ FAIL: Search query failed${NC}"
    echo -e "  ${YELLOW}💡 Response code: $search_code${NC}"
fi

sleep 0.5

# Test 6: Query History
echo -e "\n${YELLOW}[6/6] Testing Query History...${NC}"
history_response=$(curl -s -w "\n%{http_code}" "$BASE_URL/history?page=1&page_size=5")
history_code=$(echo "$history_response" | tail -n1)
history_body=$(echo "$history_response" | sed '$d')

if [ "$history_code" = "200" ]; then
    total_queries=$(echo "$history_body" | grep -o '"total":[0-9]*' | cut -d':' -f2)
    if [ ! -z "$total_queries" ]; then
        echo -e "  ${GREEN}✅ PASS: Query history retrieved${NC}"
        echo -e "  ${GRAY}📊 Total Queries: $total_queries${NC}"
        ((PASS_COUNT++))
    else
        echo -e "  ${YELLOW}⚠️  WARN: No query history found${NC}"
    fi
else
    echo -e "  ${RED}❌ FAIL: Cannot retrieve query history${NC}"
fi

# Summary
echo -e "\n${CYAN}"
echo "============================================"
echo "📊 Test Results Summary"
echo "============================================"
echo -e "${NC}"

success_rate=$(awk "BEGIN {printf \"%.1f\", ($PASS_COUNT / $TOTAL_TESTS) * 100}")

if [ "$PASS_COUNT" -eq "$TOTAL_TESTS" ]; then
    echo -e "${GREEN}Tests Passed: $PASS_COUNT / $TOTAL_TESTS${NC}"
    echo -e "${GREEN}Success Rate: $success_rate%${NC}"
    echo ""
    echo -e "${GREEN}🎉 ALL TESTS PASSED! System is fully functional.${NC}"
    echo -e "${GREEN}✅ The AI Legal Assistant is ready for production use.${NC}"
elif [ "$PASS_COUNT" -ge 4 ]; then
    echo -e "${YELLOW}Tests Passed: $PASS_COUNT / $TOTAL_TESTS${NC}"
    echo -e "${YELLOW}Success Rate: $success_rate%${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  MOST TESTS PASSED. Some features may need attention.${NC}"
    echo -e "${YELLOW}💡 Review the failed tests above for details.${NC}"
else
    echo -e "${RED}Tests Passed: $PASS_COUNT / $TOTAL_TESTS${NC}"
    echo -e "${RED}Success Rate: $success_rate%${NC}"
    echo ""
    echo -e "${RED}❌ MULTIPLE TESTS FAILED. Please troubleshoot the issues.${NC}"
    echo -e "${YELLOW}💡 Check that:${NC}"
    echo -e "${YELLOW}   1. Server is running: python -m app.main${NC}"
    echo -e "${YELLOW}   2. API keys are set in .env file${NC}"
    echo -e "${YELLOW}   3. Dependencies are installed: pip install -r requirements.txt${NC}"
fi

echo -e "\n${CYAN}============================================${NC}\n"
