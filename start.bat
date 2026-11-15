@echo off
REM Local launcher for Windows. Docker is optional and not used here.
setlocal EnableExtensions
cd /d "%~dp0"

where py >nul 2>&1
if errorlevel 1 (
  echo Python 3.12 or newer is required. Install it from python.org, then try again.
  exit /b 1
)
where npm >nul 2>&1
if errorlevel 1 (
  echo Node.js and npm are required. Install Node.js, then try again.
  exit /b 1
)

if not exist ".env" (
  copy /Y ".env.example" ".env" >nul
  echo Created .env from .env.example.
  echo Set a unique SECRET_KEY ^(at least 32 random bytes^) in .env, then run start.bat again.
  exit /b 1
)

for /f "tokens=1,* delims==" %%A in ('findstr /b /c:"SECRET_KEY=" .env') do set "AGRISPACE_SECRET=%%B"
if "%AGRISPACE_SECRET%"=="" (
  echo Refusing to start without SECRET_KEY in .env.
  exit /b 1
)
if "%AGRISPACE_SECRET%"=="replace-with-a-32-byte-secret" (
  echo Refusing to start with the sample SECRET_KEY. Set a unique secret in .env first.
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m pip install --quiet -r backend\requirements.txt
if errorlevel 1 exit /b 1

if not exist "frontend\node_modules" (
  pushd frontend
  call npm install
  popd
  if errorlevel 1 exit /b 1
)

if not exist ".run" mkdir .run
start "AgriSpace API" /B cmd /c ".venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 > .run\api.log 2>&1"
start "AgriSpace Web" /B cmd /c "cd frontend && npm run dev > ..\.run\web.log 2>&1"

echo.
echo AgriSpace is running without Docker.
echo Web: http://localhost:5173
echo API docs: http://localhost:8000/docs
echo Logs: .run\api.log and .run\web.log
endlocal
