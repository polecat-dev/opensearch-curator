@echo off
REM Start OpenSearch test environment (Windows)

set COMPOSE_FILE=test-environments/compose/docker-compose.test.yml
set ENDPOINT=https://localhost:19200

echo Starting OpenSearch test environment...
docker-compose -f %COMPOSE_FILE% up -d

echo Waiting for OpenSearch to be healthy...
:wait_loop
timeout /t 2 /nobreak > nul
curl.exe -k -s %ENDPOINT%/_cluster/health > nul 2>&1
if %errorlevel% neq 0 (
    echo .
    goto wait_loop
)

echo.
echo OpenSearch is running!
echo To stop: scripts\stop-opensearch.bat
echo To view logs: docker-compose -f %COMPOSE_FILE% logs -f opensearch
