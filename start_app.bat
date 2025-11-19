@echo off
REM Start Flask App with Supabase Environment Variables
REM This script sets the environment variables and starts your Flask application

echo Setting Supabase environment variables...

REM Set Supabase credentials
set SUPABASE_URL=https://nwweilelmzickmmmmhmb.supabase.co
set SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im53d2VpbGVsbXppY2ttbW1taG1iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM1MjY3MjksImV4cCI6MjA3OTEwMjcyOX0.Vq99eRVvSYwj-sehc193U1nnL2EvlvE1MaCMjEeqq3s

echo SUPABASE_URL = %SUPABASE_URL%
echo SUPABASE_KEY = %SUPABASE_KEY:~0,20%...
echo.
echo Starting Flask application...
echo.

REM Start Flask app
python app.py

pause

