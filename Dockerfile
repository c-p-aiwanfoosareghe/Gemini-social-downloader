# Use a Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy all files from your repo root to the container working directory
# Since your code is in 'app/', it will copy app/, requirements.txt, etc.
COPY . .

# Install dependencies (yt-dlp, instaloader, uvicorn)
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (optional, but good practice)
EXPOSE 8000

# This is the command that Render runs by default (the equivalent of "Start Command")
# It runs the server using the python module command and the correct path: app.main:app
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
