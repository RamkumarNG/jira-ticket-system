FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY ../ ./

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Start your FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
