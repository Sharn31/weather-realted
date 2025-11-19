@echo off
REM Quick script to set Supabase environment variables for current session
REM Run this before starting your Flask app

set SUPABASE_URL=https://nwweilelmzickmmmmhmb.supabase.co
set SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im53d2VpbGVsbXppY2ttbW1taG1iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM1MjY3MjksImV4cCI6MjA3OTEwMjcyOX0.Vq99eRVvSYwj-sehc193U1nnL2EvlvE1MaCMjEeqq3s

echo Supabase environment variables set!
echo.
echo SUPABASE_URL = %SUPABASE_URL%
echo SUPABASE_KEY = %SUPABASE_KEY%
echo.
echo You can now run your Flask application.
echo Note: These are set for this terminal session only.
echo.

