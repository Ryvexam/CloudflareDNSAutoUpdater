FROM python:3.9-slim
LABEL authors="VERY Maxime"

WORKDIR /app

# Install required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./config /app/

# Run the script
CMD ["python", "ip_updater.py"]
