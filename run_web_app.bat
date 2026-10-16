@echo off
title Web URL Request Count Dashboard
echo ==========================================================
echo Starting Web URL Request Count - MapReduce Web Dashboard
echo ==========================================================
echo.
echo Starting Python Flask server...
start http://127.0.0.1:5000
python app.py
pause
