"""
HuggingFace Spaces entry point.
HF Spaces looks for app.py in root — this just calls the real UI.
"""
import subprocess
import sys

subprocess.run([
    sys.executable, "-m", "streamlit", "run",
    "ui/app.py", "--server.port", "7860",
    "--server.address", "0.0.0.0"
])
