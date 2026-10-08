@echo off
rem Opens the Short Studio through a local web server (http://localhost:8765).
rem Only needed once Frank's service is locked to sidefrog.com and allows http://localhost:8765.
cd /d "%~dp0.."
start "" http://localhost:8765/tools/frank-short-studio.html
python -m http.server 8765
