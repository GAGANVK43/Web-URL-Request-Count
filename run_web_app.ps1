Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Starting Web URL Request Count - MapReduce Web Dashboard" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""
Start-Process "http://127.0.0.1:5000"
python app.py
