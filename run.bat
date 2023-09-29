@echo off
start /B cmd /C "py casino.py"
start /B cmd /C "py pay_service.py"
start /B cmd /C "py pay_service_db.py"

echo Press Ctrl+C to terminate all processes...

:: Wait for Ctrl+C to be pressed
:waitForCtrlC
timeout /t 1 /nobreak > NUL

:: Define the names of Python files to terminate
set "file_names= casino.py pay_service.py pay_service_db.py"

:: Use wmic to get the PIDs and executable paths of Python processes
for /f "tokens=1,9 delims=," %%a in ('wmic process where "commandline like '%%python%%'" get processid,executablepath /format:csv ^| findstr /r "[0-9]"') do (
  set "pid=%%a"
  set "path=%%~nb"

  :: Check if the executable path contains any of the specified file names
  for %%f in (%file_names%) do (
    if /i "%%~nf"=="%%~f" (
      taskkill /F /PID !pid!
    )
  )
)
