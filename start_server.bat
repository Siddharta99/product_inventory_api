@echo off
cd /d "%~dp0"
py -3.10 -m uvicorn api:app --reload --port 9000
pause