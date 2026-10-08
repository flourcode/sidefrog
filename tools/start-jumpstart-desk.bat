@echo off
rem Opens the Jumpstart Desk through a local web server (http://localhost:8765), like the Short Studio.
cd /d "%~dp0.."
start "" http://localhost:8765/tools/jumpstart-desk.html
python -m http.server 8765
