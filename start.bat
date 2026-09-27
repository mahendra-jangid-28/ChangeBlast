@echo off
echo Starting ChangeBlast...
echo.
echo [1/2] Starting backend on http://localhost:8000
start "ChangeBlast Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --port 8000 --reload"

echo [2/2] Starting frontend on http://localhost:5173
timeout /t 2 /nobreak > nul
start "ChangeBlast Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ============================================
echo  ChangeBlast is starting up!
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:5173
echo  API Docs: http://localhost:8000/docs
echo ============================================
echo.
pause
