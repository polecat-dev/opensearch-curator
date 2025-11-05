@echo off
REM Start OpenSearch test environment (Windows)

echo Starting OpenSearch test environment...

docker-compose up -d

echo Waiting for OpenSearch to be healthy...

:wait_loop
timeout /t 2 /nobreak > nul
curl -f -s http://localhost:9200/_cluster/health > nul 2>&1
if %errorlevel% neq 0 (
    echo .
    goto wait_loop
)

echo.
echo OpenSearch is running!
echo.
echo Cluster health:
curl -s http://localhost:9200/_cluster/health?pretty
echo.
echo OpenSearch: http://localhost:9200
echo Dashboards: http://localhost:5601
echo.
echo To stop: scripts\stop-opensearch.bat
