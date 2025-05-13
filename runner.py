# dev_runner.py
import subprocess
import time
import os
import signal

# Optional: customize paths if you ever move frontend/backend
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = ROOT_DIR  # assuming frontend is root-level (Next.js project)

def start_process(name, cmd, cwd):
    print(f"🚀 Starting {name}...")
    return subprocess.Popen(
        cmd,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid  # so we can kill the whole process group on exit
    )

def stream_output(process, name):
    for line in iter(process.stdout.readline, b''):
        print(f"[{name}] {line.decode().rstrip()}")

# Launch all services
processes = []

try:
    processes.append(("Scheduler", start_process("Scheduler", "python3 scheduler.py", os.path.join(BACKEND_DIR, "signals"))))
    time.sleep(5)
    processes.append(("Backend", start_process("Backend", "uvicorn backend.main:app --reload --port 8000", ROOT_DIR)))
    time.sleep(5)
    processes.append(("Frontend", start_process("Frontend", "npm run dev", FRONTEND_DIR)))

    print("✅ All services started. Press Ctrl+C to shut down.\n")

    # Keep running until interrupted
    while True:
        time.sleep(5)

except KeyboardInterrupt:
    print("\n🛑 Shutting down all services...")
    for name, proc in processes:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            print(f"✔️  {name} terminated.")
        except Exception as e:
            print(f"⚠️ Error terminating {name}: {e}")
