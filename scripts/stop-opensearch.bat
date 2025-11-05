@echo off
REM Stop OpenSearch test environment (Windows)

echo Stopping OpenSearch test environment...

docker-compose down

echo OpenSearch stopped
echo.
echo To remove all data: docker-compose down -v
