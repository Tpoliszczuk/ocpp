FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 8000 for WebSocket connections
EXPOSE 8000

# Set environment variable for port
ENV PORT=8000

CMD ["python", "server.py"]
