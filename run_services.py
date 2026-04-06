"""
run_services.py  — Robust service launcher for Vision-First AutoGrader
Starts OCR (8001), Grading (8003), and Analytics (8004).
Auto-restarts on crash. Press Ctrl+C to stop all.
"""
import subprocess, time, sys, os
import requests

BASE   = r"c:\Users\tallu\OneDrive\Desktop\AutoGrader"
PYTHON = r"C:\Users\tallu\anaconda3\python.exe"

# Kill any existing AutoGrader service processes via taskkill
print("Stopping any existing service processes...")
os.system('wmic process where "name=\'python.exe\' and commandline like \'%AutoGrader%main.py%\'" call terminate >nul 2>&1')
time.sleep(2)

SERVICES = [
    {
        "name": "Zone Cropper (8001)",
        "port": 8001,
        "dir":  rf"{BASE}\ml-services\ocr-service",
        "log":  rf"{BASE}\ml-services\ocr-service\svc_out.log",
    },
    {
        "name": "Vision Grader (8003)",
        "port": 8003,
        "dir":  rf"{BASE}\ml-services\grading-engine",
        "log":  rf"{BASE}\ml-services\grading-engine\svc_out.log",
    },
    {
        "name": "Analytics (8004)",
        "port": 8004,
        "dir":  rf"{BASE}\ml-services\analytics-engine",
        "log":  rf"{BASE}\ml-services\analytics-engine\svc_out.log",
    },
]


def start_service(svc: dict):
    # Ensure log file exists or is clear
    if not os.path.exists(os.path.dirname(svc["log"])):
        os.makedirs(os.path.dirname(svc["log"]))
        
    log_f = open(svc["log"], "a", encoding="utf-8")
    p = subprocess.Popen(
        [PYTHON, "main.py"],
        cwd=svc["dir"],
        stdout=log_f,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    print(f"  Started {svc['name']} PID={p.pid}")
    return p, log_f


def is_healthy(port: int) -> bool:
    try:
        # Check health endpoint
        return requests.get(f"http://localhost:{port}/health", timeout=2).status_code == 200
    except Exception:
        return False


# ── Start all services ────────────────────────────────────────────────────────
procs = []
print("\nLaunching Vision-First Orchestrator Services...")
for svc in SERVICES:
    p, log_f = start_service(svc)
    procs.append({"svc": svc, "proc": p, "log_f": log_f})

print(f"\nWaiting 5s for services to initialise (Fast Startup Mode)...")
time.sleep(5)

# ── Initial health check ──────────────────────────────────────────────────────
for srv in SERVICES:
    ok = is_healthy(srv["port"])
    print(f"  {srv['name']}: {'UP ✓' if ok else 'DOWN ✗ (Check logs)'}")

print("\nWatchdog active — press Ctrl+C to stop.\n")

# ── Watchdog loop ─────────────────────────────────────────────────────────────
try:
    while True:
        time.sleep(10)
        for entry in procs:
            if entry["proc"].poll() is not None:  # process exited
                svc = entry["svc"]
                code = entry["proc"].returncode
                print(f"[RESTART] {svc['name']} exited (code {code}) — restarting...")
                entry["log_f"].close()
                new_p, new_log = start_service(svc)
                entry["proc"]  = new_p
                entry["log_f"] = new_log
except KeyboardInterrupt:
    print("\nShutting down...")
    for entry in procs:
        try:
            entry["proc"].terminate()
            entry["log_f"].close()
            print(f"  Stopped {entry['svc']['name']}")
        except Exception:
            pass
