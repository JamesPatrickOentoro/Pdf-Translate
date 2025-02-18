# Use Python 3.10 (Compatible with PyTorch)
FROM python:3.12-slim

# Set working directory
WORKDIR /app


# Copy and install dependencies from requirements.txt (torch should NOT be in this file)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
EXPOSE 7860
# Set default command to run the application
CMD ["python", "main.py", "--server.port", "7860"]
