# OpenSearch Curator - Local Test Data Creator
# Creates sample indices for testing curator actions

# Configuration
$opensearchUrl = "https://localhost:19200"
$indexPrefix = "test-"

# Date range: Create indices for last 30 days
$days = 30
$today = Get-Date

Write-Host "Creating test indices in OpenSearch at $opensearchUrl" -ForegroundColor Cyan
Write-Host "Prefix: $indexPrefix" -ForegroundColor Cyan
Write-Host "Date range: Last $days days" -ForegroundColor Cyan
Write-Host ""

# Function to create index with timestamp
function Create-TestIndex {
    param(
        [string]$IndexName,
        [DateTime]$Date
    )
    
    $body = @{
        settings = @{
            number_of_shards = 1
            number_of_replicas = 1
        }
        mappings = @{
            properties = @{
                timestamp = @{
                    type = "date"
                }
                message = @{
                    type = "text"
                }
                level = @{
                    type = "keyword"
                }
            }
        }
    } | ConvertTo-Json -Depth 10
    
    try {
        $response = Invoke-RestMethod -Uri "$opensearchUrl/$IndexName" -Method Put -Body $body -ContentType "application/json" -ErrorAction Stop
        
        if ($response.acknowledged) {
            Write-Host "  [OK] Created: $IndexName" -ForegroundColor Green
            
            # Add a sample document
            $doc = @{
                timestamp = $Date.ToString("yyyy-MM-ddTHH:mm:ssZ")
                message = "Sample log entry for $($Date.ToString('yyyy-MM-dd'))"
                level = "INFO"
            } | ConvertTo-Json
            
            Invoke-RestMethod -Uri "$opensearchUrl/$IndexName/_doc/1" -Method Post -Body $doc -ContentType "application/json" | Out-Null
        }
    }
    catch {
        Write-Host "  [FAIL] Failed: $IndexName - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Create indices for each day
Write-Host "Creating indices..." -ForegroundColor Yellow
for ($i = 0; $i -lt $days; $i++) {
    $date = $today.AddDays(-$i)
    $indexName = "$indexPrefix$($date.ToString('yyyy.MM.dd'))"
    Create-TestIndex -IndexName $indexName -Date $date
}

Write-Host ""
Write-Host "Creating additional log indices..." -ForegroundColor Yellow

# Create some logs-* indices too
$logDays = 10
for ($i = 0; $i -lt $logDays; $i++) {
    $date = $today.AddDays(-$i)
    $indexName = "logs-$($date.ToString('yyyy.MM.dd'))"
    Create-TestIndex -IndexName $indexName -Date $date
}

# Summary
Write-Host ""
Write-Host "Test data creation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Verify with:" -ForegroundColor Cyan
Write-Host "  curl $opensearchUrl/_cat/indices?v" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Run: curator --config curator.yml 01-list-all-indices.yml --dry-run" -ForegroundColor White
Write-Host "  2. Test other action files" -ForegroundColor White
Write-Host "  3. See README.md for full guide" -ForegroundColor White
