@echo off

echo Starting Backend...
REM Replace D:\rag_project\backend with the full path to your project's backend folder.
start cmd /k "cd /d D:\rag_project\backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000"

timeout /t 3 > nul

echo Starting Frontend...
REM Replace D:\rag_project\frontend with the full path to your project's frontend folder.
start cmd /k "cd /d D:\rag_project\frontend && npm run dev"

echo Project Started!
pause
