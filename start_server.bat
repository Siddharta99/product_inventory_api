   @echo off
   cd /d "%~dp0"
   uvicorn api:app --reload --port 9000
   pause