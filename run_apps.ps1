# PowerShell script to start backend and frontend services for the project

# 1. activate Python environment
& .\ml_env\Scripts\Activate.ps1

# 2. launch backend in a separate window so we can start frontend concurrently
Start-Process powershell -ArgumentList '-NoExit','-Command','cd 6_dashboard\backend_api; uvicorn app:app --reload --host 127.0.0.1 --port 8000'

# 3. start frontend in the current window
cd 6_dashboard\frontend_web
npm start
