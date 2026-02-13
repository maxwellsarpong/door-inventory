import subprocess
import sys
import webbrowser
import time
import os

def main():
    port = "8501"

    # Start Streamlit
    subprocess.Popen([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.port",
        port,
        "--server.headless",
        "true"
    ], cwd=os.path.dirname(__file__))

    # Wait for server to start
    time.sleep(3)

    # Open browser
    webbrowser.open(f"http://localhost:{port}")

if __name__ == "__main__":
    main()
