# Use an official Python runtime as a parent image
FROM python:3.11-slim

# ... (Lines before this are fine)

# Set the working directory (e.g., /usr/src/app)
WORKDIR /usr/src/app 

# Copy all files from the root of your repo into the container
COPY . . 

# Run the correct command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
