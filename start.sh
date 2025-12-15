#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status.
set -o errexit

# 1. Install dependencies (if your Build Command is failing, this ensures it runs)
pip install -r requirements.txt

# 2. Run the server using the module path, which is often more reliable
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
