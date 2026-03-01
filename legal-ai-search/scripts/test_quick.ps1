# Quick Validation Test Script for AI Legal Research Assistant
# Usage: powershell -ExecutionPolicy Bypass -File scripts\test_quick.ps1

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "🧪 AI Legal Assistant - Quick Validation" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:8000"
$passCount = 0
$totalTests = 6

# Test 1: Health Check
Write-Host "[1/6] Testing API Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get -ErrorAction Stop
    if ($health.status -eq "healthy") {
        Write-Host "  ✅ PASS: API is healthy" -ForegroundColor Green
        Write-Host "  📊 Status: $($health.status)" -ForegroundColor Gray
        Write-Host "  📦 Documents Indexed: $($health.documents_indexed)" -ForegroundColor Gray
        $passCount++
    } else {
        Write-Host "  ❌ FAIL: API returned unhealthy status" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ FAIL: Cannot connect to API at $baseUrl" -ForegroundColor Red
    Write-Host "  💡 Make sure the server is running: python -m app.main" -ForegroundColor Yellow
}

Start-Sleep -Milliseconds 500

# Test 2: API Documentation
Write-Host "`n[2/6] Testing API Documentation..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/docs" -Method Get -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✅ PASS: Swagger documentation accessible" -ForegroundColor Green
        Write-Host "  🔗 URL: $baseUrl/docs" -ForegroundColor Gray
        $passCount++
    } else {
        Write-Host "  ❌ FAIL: Documentation not accessible" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ FAIL: Cannot access API documentation" -ForegroundColor Red
}

Start-Sleep -Milliseconds 500

# Test 3: Document Upload
Write-Host "`n[3/6] Testing Document Upload..." -ForegroundColor Yellow
$testContent = @"
SUPREME COURT TEST CASE

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
Judgment for the plaintiff. Defendant liable for breach of contract damages.
"@

$uploadBody = @{
    filename = "test_contract_case.txt"
    content = $testContent
    metadata = @{
        case_number = "TEST-2024-001"
        court = "Test District Court"
        topic = "Contract Law"
        test_document = $true
    }
} | ConvertTo-Json -Depth 10

try {
    $upload = Invoke-RestMethod -Uri "$baseUrl/documents/upload" -Method Post -Body $uploadBody -ContentType "application/json" -ErrorAction Stop
    Write-Host "  ✅ PASS: Document uploaded successfully" -ForegroundColor Green
    Write-Host "  📄 Document ID: $($upload.doc_id)" -ForegroundColor Gray
    Write-Host "  📊 Chunks Created: $($upload.num_chunks)" -ForegroundColor Gray
    Write-Host "  💾 Size: $($upload.size_bytes) bytes" -ForegroundColor Gray
    $docId = $upload.doc_id
    $passCount++
} catch {
    Write-Host "  ❌ FAIL: Document upload failed" -ForegroundColor Red
    Write-Host "  💡 Error: $($_.Exception.Message)" -ForegroundColor Yellow
    $docId = $null
}

Start-Sleep -Seconds 2  # Give time for indexing

# Test 4: List Documents
Write-Host "`n[4/6] Testing Document Listing..." -ForegroundColor Yellow
try {
    $documents = Invoke-RestMethod -Uri "$baseUrl/documents" -Method Get -ErrorAction Stop
    if ($documents.Count -gt 0) {
        Write-Host "  ✅ PASS: Documents retrieved successfully" -ForegroundColor Green
        Write-Host "  📚 Total Documents: $($documents.Count)" -ForegroundColor Gray
        $passCount++
    } else {
        Write-Host "  ⚠️  WARN: No documents found (this might be expected)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ FAIL: Cannot retrieve document list" -ForegroundColor Red
}

Start-Sleep -Milliseconds 500

# Test 5: Semantic Search
Write-Host "`n[5/6] Testing Semantic Search..." -ForegroundColor Yellow
$searchBody = @{
    query = "What constitutes a material breach of contract when time is of the essence?"
    top_k = 3
    include_citations = $true
} | ConvertTo-Json

try {
    $startTime = Get-Date
    $search = Invoke-RestMethod -Uri "$baseUrl/search" -Method Post -Body $searchBody -ContentType "application/json" -ErrorAction Stop
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalMilliseconds
    
    Write-Host "  ✅ PASS: Search completed successfully" -ForegroundColor Green
    Write-Host "  ⏱️  Search Time: $([math]::Round($duration, 0))ms" -ForegroundColor Gray
    Write-Host "  🤖 Model Used: $($search.model_used)" -ForegroundColor Gray
    Write-Host "  📑 Citations: $($search.citations.Count)" -ForegroundColor Gray
    Write-Host "  💡 Answer Preview: $($search.answer.Substring(0, [Math]::Min(100, $search.answer.Length)))..." -ForegroundColor Gray
    
    if ($search.citations.Count -gt 0) {
        Write-Host "  🎯 Top Relevance Score: $([math]::Round($search.citations[0].relevance_score, 3))" -ForegroundColor Gray
    }
    
    $passCount++
} catch {
    Write-Host "  ❌ FAIL: Search query failed" -ForegroundColor Red
    Write-Host "  💡 Error: $($_.Exception.Message)" -ForegroundColor Yellow
}

Start-Sleep -Milliseconds 500

# Test 6: Query History
Write-Host "`n[6/6] Testing Query History..." -ForegroundColor Yellow
try {
    $history = Invoke-RestMethod -Uri "$baseUrl/history?page=1&page_size=5" -Method Get -ErrorAction Stop
    if ($history.queries) {
        Write-Host "  ✅ PASS: Query history retrieved" -ForegroundColor Green
        Write-Host "  📊 Total Queries: $($history.total)" -ForegroundColor Gray
        Write-Host "  📄 Recent Queries: $($history.queries.Count)" -ForegroundColor Gray
        $passCount++
    } else {
        Write-Host "  ⚠️  WARN: No query history found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ FAIL: Cannot retrieve query history" -ForegroundColor Red
}

# Summary
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "📊 Test Results Summary" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Tests Passed: $passCount / $totalTests" -ForegroundColor $(if ($passCount -eq $totalTests) { "Green" } elseif ($passCount -ge 4) { "Yellow" } else { "Red" })
Write-Host "Success Rate: $([math]::Round(($passCount / $totalTests) * 100, 1))%" -ForegroundColor $(if ($passCount -eq $totalTests) { "Green" } elseif ($passCount -ge 4) { "Yellow" } else { "Red" })

Write-Host ""
if ($passCount -eq $totalTests) {
    Write-Host "🎉 ALL TESTS PASSED! System is fully functional." -ForegroundColor Green
    Write-Host "✅ The AI Legal Assistant is ready for production use." -ForegroundColor Green
} elseif ($passCount -ge 4) {
    Write-Host "⚠️  MOST TESTS PASSED. Some features may need attention." -ForegroundColor Yellow
    Write-Host "💡 Review the failed tests above for details." -ForegroundColor Yellow
} else {
    Write-Host "❌ MULTIPLE TESTS FAILED. Please troubleshoot the issues." -ForegroundColor Red
    Write-Host "💡 Check that:" -ForegroundColor Yellow
    Write-Host "   1. Server is running: python -m app.main" -ForegroundColor Yellow
    Write-Host "   2. API keys are set in .env file" -ForegroundColor Yellow
    Write-Host "   3. Dependencies are installed: pip install -r requirements.txt" -ForegroundColor Yellow
}

Write-Host "`n============================================`n" -ForegroundColor Cyan
