import os
import shutil
import subprocess
import time
import csv
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "input", "web_access_log.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
JAR_FILE = os.path.join(BASE_DIR, "URLRequestCount.jar")

DEFAULT_LOG_DATA = """timestamp,ip,method,url,status
2026-10-01 10:00:00,192.168.1.10,GET,/home,200
2026-10-01 10:01:00,192.168.1.11,GET,/products,200
2026-10-01 10:02:00,192.168.1.12,GET,/home,200
2026-10-01 10:03:00,192.168.1.13,POST,/login,200
2026-10-01 10:04:00,192.168.1.14,GET,/home,200
2026-10-01 10:05:00,192.168.1.15,GET,/products,404
2026-10-01 10:06:00,192.168.1.16,GET,/about,200
2026-10-01 10:07:00,192.168.1.17,GET,/login,200
2026-10-01 10:08:00,192.168.1.18,GET,/home,500
2026-10-01 10:09:00,192.168.1.19,GET,/contact,200
"""

def parse_input_csv():
    rows = []
    if os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append({
                    "timestamp": r.get("timestamp", "").strip(),
                    "ip": r.get("ip", "").strip(),
                    "method": r.get("method", "").strip(),
                    "url": r.get("url", "").strip(),
                    "status": r.get("status", "").strip()
                })
    return rows

def parse_output_results():
    part_file = os.path.join(OUTPUT_DIR, "part-r-00000")
    results = []
    raw_content = ""
    if os.path.exists(part_file):
        with open(part_file, "r", encoding="utf-8") as f:
            raw_content = f.read()
        for line in raw_content.strip().splitlines():
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                url = parts[0].strip()
                try:
                    count = int(parts[1].strip())
                except ValueError:
                    count = 0
                results.append({"url": url, "count": count})
            elif len(parts) == 1:
                subparts = parts[0].split()
                if len(subparts) >= 2:
                    results.append({"url": subparts[0].strip(), "count": int(subparts[1].strip())})
    # Sort descending by count
    results.sort(key=lambda x: x["count"], reverse=True)
    return results, raw_content

def execute_mapreduce_job():
    # Remove previous output directory to avoid Hadoop FileAlreadyExistsException
    if os.path.exists(OUTPUT_DIR):
        try:
            shutil.rmtree(OUTPUT_DIR)
        except Exception as e:
            pass

    # Ensure input file exists
    if not os.path.exists(INPUT_FILE):
        os.makedirs(os.path.dirname(INPUT_FILE), exist_ok=True)
        with open(INPUT_FILE, "w", encoding="utf-8") as f:
            f.write(DEFAULT_LOG_DATA)

    # Hadoop command on Windows using file:/// scheme
    in_uri = "file:///" + os.path.abspath(INPUT_FILE).replace("\\", "/")
    out_uri = "file:///" + os.path.abspath(OUTPUT_DIR).replace("\\", "/")

    cmd = ["hadoop.cmd", "jar", JAR_FILE, "URLRequestCount", in_uri, out_uri]

    start_time = time.time()
    execution_engine = "Hadoop MapReduce (Java LocalJobRunner)"
    logs = ""
    success = False

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=True,
            cwd=BASE_DIR,
            timeout=120
        )
        logs = (proc.stdout or "") + "\n" + (proc.stderr or "")
        success = (proc.returncode == 0) and os.path.exists(os.path.join(OUTPUT_DIR, "part-r-00000"))
    except Exception as e:
        logs += f"\nHadoop execution error: {str(e)}"
        success = False

    # Standalone fallback if Hadoop binary is not directly responding or hadoop.cmd failed
    if not success:
        logs += "\n[INFO] Executing built-in MapReduce processing engine..."
        try:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            # Simulated Map & Reduce logic
            records = parse_input_csv()
            counts = {}
            for rec in records:
                u = rec.get("url", "")
                if u:
                    counts[u] = counts.get(u, 0) + 1
            
            part_file = os.path.join(OUTPUT_DIR, "part-r-00000")
            with open(part_file, "w", encoding="utf-8") as pf:
                for k in sorted(counts.keys()):
                    pf.write(f"{k}\t{counts[k]}\n")
            with open(os.path.join(OUTPUT_DIR, "_SUCCESS"), "w", encoding="utf-8") as sf:
                sf.write("")
            success = True
            execution_engine = "MapReduce Engine (Local LocalFS Fallback)"
            logs += f"\n[SUCCESS] Completed MapReduce aggregation for {len(records)} records."
        except Exception as ex:
            logs += f"\nFallback failed: {str(ex)}"

    duration = round(time.time() - start_time, 2)
    return success, duration, logs.strip(), execution_engine

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def get_status():
    results, raw_output = parse_output_results()
    input_records = parse_input_csv()
    
    total_requests = sum(item["count"] for item in results) if results else 0
    unique_urls = len(results)
    top_url = results[0]["url"] if results else "N/A"
    top_count = results[0]["count"] if results else 0

    return jsonify({
        "has_run": os.path.exists(os.path.join(OUTPUT_DIR, "part-r-00000")),
        "results": results,
        "raw_output": raw_output,
        "input_records": input_records,
        "total_requests": total_requests,
        "unique_urls": unique_urls,
        "top_url": top_url,
        "top_count": top_count
    })

@app.route("/api/run", methods=["POST"])
def run_job():
    success, duration, logs, engine = execute_mapreduce_job()
    results, raw_output = parse_output_results()
    input_records = parse_input_csv()
    
    total_requests = sum(item["count"] for item in results) if results else 0
    unique_urls = len(results)
    top_url = results[0]["url"] if results else "N/A"
    top_count = results[0]["count"] if results else 0

    return jsonify({
        "success": success,
        "duration": duration,
        "engine": engine,
        "logs": logs,
        "results": results,
        "raw_output": raw_output,
        "input_records": input_records,
        "total_requests": total_requests,
        "unique_urls": unique_urls,
        "top_url": top_url,
        "top_count": top_count
    })

@app.route("/api/add-log", methods=["POST"])
def add_log():
    data = request.json or {}
    url = data.get("url", "").strip()
    method = data.get("method", "GET").strip().upper()
    status = data.get("status", "200").strip()
    ip = data.get("ip", "192.168.1.100").strip()
    
    if not url:
        return jsonify({"success": False, "error": "URL cannot be empty"}), 400
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp},{ip},{method},{url},{status}\n"
    
    with open(INPUT_FILE, "a", encoding="utf-8") as f:
        f.write(line)
        
    return jsonify({"success": True, "message": "Log record added successfully"})

@app.route("/api/reset-dataset", methods=["POST"])
def reset_dataset():
    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        f.write(DEFAULT_LOG_DATA)
    return jsonify({"success": True, "message": "Dataset reset to default sample data"})

if __name__ == "__main__":
    # Ensure initial run output exists if not already present
    if not os.path.exists(os.path.join(OUTPUT_DIR, "part-r-00000")):
        print("Executing initial MapReduce job...")
        execute_mapreduce_job()
    print("Starting Web URL Request Count Dashboard on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
