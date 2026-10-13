import csv
import json
import logging
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request

BASE = Path(__file__).parent
DB = BASE / "automation.db"
LOG = BASE / "logs" / "automation.log"
DATA = BASE / "data"

logging.basicConfig(filename=LOG, level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS processed_files(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT, rows_processed INTEGER, status TEXT, processed_at TEXT)""")
        con.execute("""CREATE TABLE IF NOT EXISTS api_results(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT, item_count INTEGER, status TEXT, fetched_at TEXT)""")

def create_sample_csv():
    DATA.mkdir(exist_ok=True)
    sample = DATA / "sales.csv"
    if not sample.exists():
        with open(sample,"w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["product","quantity","price"])
            w.writerows([["Laptop",2,55000],["Mouse",10,700],["Keyboard",5,1200],["Monitor",3,15000]])
    return sample

def process_csv(path):
    try:
        with open(path,newline="",encoding="utf-8") as f:
            rows=list(csv.DictReader(f))
        total=sum(float(r["quantity"])*float(r["price"]) for r in rows)
        with sqlite3.connect(DB) as con:
            con.execute("""INSERT INTO processed_files(filename,rows_processed,status,processed_at)
                           VALUES(?,?,?,?,?)""",(path.name,len(rows),"SUCCESS",datetime.now().isoformat()))
        logging.info("Processed %s: %d rows, total %.2f", path.name, len(rows), total)
        return {"file":path.name,"rows":len(rows),"total":total,"status":"SUCCESS"}
    except Exception as e:
        logging.exception("Failed to process %s", path)
        return {"file":path.name,"rows":0,"total":0,"status":f"ERROR: {e}"}

def process_all_files():
    files=list(DATA.glob("*.csv"))
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(process_csv, files))
    print(json.dumps(results, indent=2))
    return results

def fetch_api():
    url="https://jsonplaceholder.typicode.com/todos"
    try:
        req=Request(url,headers={"User-Agent":"Cognevance-Automation-Demo"})
        with urlopen(req, timeout=10) as response:
            data=json.loads(response.read().decode())
        with sqlite3.connect(DB) as con:
            con.execute("""INSERT INTO api_results(endpoint,item_count,status,fetched_at)
                           VALUES(?,?,?,?)""",(url,len(data),"SUCCESS",datetime.now().isoformat()))
        logging.info("API fetched successfully: %d items",len(data))
        print(f"API success: received {len(data)} records.")
        return data
    except Exception as e:
        logging.exception("API request failed")
        print("API request failed:",e)
        return []

def generate_report():
    with sqlite3.connect(DB) as con:
        files=con.execute("""SELECT filename,rows_processed,status,processed_at
                             FROM processed_files ORDER BY id DESC""").fetchall()
        apis=con.execute("""SELECT endpoint,item_count,status,fetched_at
                            FROM api_results ORDER BY id DESC""").fetchall()
    report={
        "generated_at":datetime.now().isoformat(),
        "processed_files":files,
        "api_results":apis
    }
    out=BASE/"reports"/"automation_report.json"
    out.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("Report:",out)
    return report

def send_notification(message):
    # Safe local notification placeholder. Configure SMTP in email_notification.py if required.
    notification=BASE/"reports"/"notification.txt"
    notification.write_text(
        f"Enterprise Automation Notification\n{datetime.now().isoformat()}\n\n{message}\n",
        encoding="utf-8")
    logging.info("Notification generated.")
    print("Notification generated:", notification)

def dashboard():
    try:
        from flask import Flask, jsonify, render_template_string
    except ImportError:
        print("Install Flask: pip install -r requirements.txt")
        return
    app=Flask(__name__)
    HTML="""<!doctype html><html><head><title>Automation Dashboard</title>
    <style>body{font-family:Arial;margin:40px}table{border-collapse:collapse;width:100%}
    td,th{border:1px solid #ccc;padding:8px}th{background:#eee}</style></head>
    <body><h1>Enterprise Automation Dashboard</h1>
    <p>Monitoring processed files and API activity.</p>
    <h2>Processed Files</h2><table><tr><th>File</th><th>Rows</th><th>Status</th><th>Time</th></tr>
    {% for r in files %}<tr>{% for x in r %}<td>{{x}}</td>{% endfor %}</tr>{% endfor %}</table>
    <h2>API Results</h2><table><tr><th>Endpoint</th><th>Items</th><th>Status</th><th>Time</th></tr>
    {% for r in apis %}<tr>{% for x in r %}<td>{{x}}</td>{% endfor %}</tr>{% endfor %}</table>
    </body></html>"""
    @app.route("/")
    def home():
        with sqlite3.connect(DB) as con:
            files=con.execute("SELECT filename,rows_processed,status,processed_at FROM processed_files ORDER BY id DESC").fetchall()
            apis=con.execute("SELECT endpoint,item_count,status,fetched_at FROM api_results ORDER BY id DESC").fetchall()
        return render_template_string(HTML,files=files,apis=apis)
    @app.route("/api/status")
    def status():
        with sqlite3.connect(DB) as con:
            count=con.execute("SELECT COUNT(*) FROM processed_files").fetchone()[0]
        return jsonify({"processed_files":count,"time":datetime.now().isoformat()})
    print("Dashboard running at http://127.0.0.1:5000")
    app.run(debug=False)

def scheduled_job():
    process_all_files()
    fetch_api()
    generate_report()
    send_notification("Scheduled automation job completed successfully.")

def main():
    init_db()
    create_sample_csv()
    while True:
        print("\n=== ENTERPRISE AUTOMATION & DATA PROCESSING SYSTEM ===")
        print("1 Process CSV files")
        print("2 Fetch external API")
        print("3 Generate report")
        print("4 Run complete automation workflow")
        print("5 Start dashboard")
        print("6 Exit")
        c=input("Choice: ").strip()
        if c=="1": process_all_files()
        elif c=="2": fetch_api()
        elif c=="3": generate_report()
        elif c=="4": scheduled_job()
        elif c=="5": dashboard()
        elif c=="6": break
        else: print("Invalid choice.")

if __name__=="__main__":
    main()
