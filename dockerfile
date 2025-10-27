# Use an official Python runtime as a base image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8000

# Define environment variable (can be overridden by Render)
ENV PYTHONPATH=/app

# Run the application with Uvicorn, optimized for production
# Using 1 worker per core is best practice in containers. Render will scale horizontally.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
