# Web URL Request Count using Hadoop MapReduce & Web Dashboard

## Objective
Count web requests received by each URL using Java and Hadoop MapReduce, and view the results in an interactive real-time web dashboard.

## Technologies
- Java 17 / Java 11
- Apache Hadoop 3.5.0
- Hadoop MapReduce (LocalJobRunner)
- Python 3 & Flask (Web Dashboard Backend)
- Tailwind CSS & Chart.js (Web UI & Analytics)

## Project Files
- `src/` - Java Mapper (`URLRequestMapper.java`), Reducer (`URLRequestReducer.java`), and driver (`URLRequestCount.java`)
- `URLRequestCount.jar` - Pre-compiled MapReduce Jar
- `input/web_access_log.csv` - Sample access log dataset
- `app.py` - Flask web application backend
- `templates/index.html` - Interactive web dashboard interface
- `run_web_app.bat` - One-click Windows launch script
- `run_web_app.ps1` - PowerShell launch script
- `output/part-r-00000` - Aggregated MapReduce output

## Quick Start (Web Dashboard)

### Method 1: Double-click Batch File
Double click `run_web_app.bat` to launch the server and automatically open the dashboard in your default browser.

### Method 2: Command Line
```powershell
python app.py
```
Open your browser and navigate to:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

### Web Dashboard Features
- **One-Click Execution**: Press **"Execute MapReduce"** to trigger Hadoop processing locally.
- **Visual Analytics**: Interactive Bar and Donut charts showing traffic distribution and request volume.
- **Results Table**: Breakdown of each URL, request count, and percentage share.
- **Log Inspector**: View existing `web_access_log.csv` records.
- **Add Access Log Entries**: Add custom endpoint hits on the fly and re-run MapReduce to see updated statistics immediately.
- **Console Logs & Raw Output**: View the raw `part-r-00000` file and live Hadoop LocalJobRunner terminal logs.

---

## Command Line Execution (Hadoop CLI)
To run the MapReduce job directly from the terminal without the web server:

```powershell
# Remove old output directory if it exists
Remove-Item -Recurse -Force output -ErrorAction SilentlyContinue

# Run Hadoop MapReduce locally
hadoop.cmd jar URLRequestCount.jar URLRequestCount file:///$((Get-Item "input/web_access_log.csv").FullName -replace '\\', '/') file:///$((Get-Item .).FullName -replace '\\', '/')/output

# View generated results
Get-Content output/part-r-00000
```

## Expected Output
```text
/about      1
/contact    1
/home       4
/login      2
/products   2
```
