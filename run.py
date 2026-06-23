import subprocess
import sys
import os
import time
import threading

def log_output(process, prefix):
    for line in iter(process.stdout.readline, ''):
        if line:
            sys.stdout.write(f"[{prefix}] {line}")
            sys.stdout.flush()

def main():
    print("=" * 60)
    print("           HealthSphere AI Startup Manager")
    print("=" * 60)
    
    # Paths to virtual environment executables on Windows
    venv_python = os.path.join("venv", "Scripts", "python.exe")
    venv_uvicorn = os.path.join("venv", "Scripts", "uvicorn.exe")
    venv_streamlit = os.path.join("venv", "Scripts", "streamlit.exe")
    
    if not os.path.exists(venv_python):
        print("Error: Virtual environment not found. Please create it first.")
        sys.exit(1)
        
    print("[System] Starting FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_cmd = [
        venv_uvicorn, 
        "backend.app.main:app", 
        "--host", "127.0.0.1", 
        "--port", "8000"
    ]
    
    backend_proc = subprocess.Popen(
        backend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Thread to log backend output
    backend_thread = threading.Thread(target=log_output, args=(backend_proc, "Backend"), daemon=True)
    backend_thread.start()
    
    # Wait a few seconds for backend to start before launching frontend
    time.sleep(3)
    
    print("[System] Starting Streamlit Frontend on http://127.0.0.1:8501 ...")
    frontend_cmd = [
        venv_streamlit,
        "run",
        "frontend/app.py",
        "--server.port", "8501",
        "--server.address", "127.0.0.1"
    ]
    
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Thread to log frontend output
    frontend_thread = threading.Thread(target=log_output, args=(frontend_proc, "Frontend"), daemon=True)
    frontend_thread.start()
    
    print("[System] HealthSphere AI is fully running!")
    print("[System] Press Ctrl+C to stop both processes.")
    print("=" * 60)
    
    try:
        while True:
            # Check if any process died
            if backend_proc.poll() is not None:
                print("[System] Backend crashed! Stopping all services.")
                break
            if frontend_proc.poll() is not None:
                print("[System] Frontend crashed! Stopping all services.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[System] Shutting down processes...")
    finally:
        # Graceful shutdown
        backend_proc.terminate()
        frontend_proc.terminate()
        try:
            backend_proc.wait(timeout=2)
            frontend_proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            backend_proc.kill()
            frontend_proc.kill()
        print("[System] All processes stopped. Goodbye!")

if __name__ == "__main__":
    main()
