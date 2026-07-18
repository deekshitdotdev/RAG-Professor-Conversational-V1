@echo off

echo Starting Backend...
start cmd /k "cd /d D:\rag_project\backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000"

timeout /t 3 > nul

echo Starting Frontend...
start cmd /k "cd /d D:\rag_project\frontend && npm run dev"

echo Project Started!
pause