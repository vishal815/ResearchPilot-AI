# ── ResearchPilot AI — Hugging Face Spaces Dockerfile ─────────
# Python 3.11 slim keeps the image small (~600MB vs ~1.2GB full)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# System dependencies for:
#   build-essential → compiles some Python C-extensions (reportlab, etc.)
#   libglib2.0-0    → required by kaleido's headless Chromium (chart→PNG)
#   libgl1-mesa-glx → also required by kaleido
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (Docker layer caching —
# only re-runs if requirements.txt changes, not on every code change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Hugging Face Spaces runs on port 7860
EXPOSE 7860

# LangSmith tracing env vars (values come from HF Secrets at runtime)
# Setting the project name here so it's always consistent in the trace view
ENV LANGCHAIN_PROJECT="researchpilot-ai"

# Start Streamlit on the HF Spaces expected port
CMD ["streamlit", "run", "ui/app.py", \
     "--server.port", "7860", \
     "--server.address", "0.0.0.0", \
     "--server.headless", "true", \
     "--browser.gatherUsageStats", "false"]
