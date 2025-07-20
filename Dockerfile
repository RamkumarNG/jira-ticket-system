FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Make start.sh executable
RUN chmod +x app/start_server.sh

# Set environment variables if needed
ENV PYTHONUNBUFFERED=1

# Start with the script
CMD ["./app/start_server.sh"]

