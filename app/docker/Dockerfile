# app/docker/Dockerfile

FROM python:3.8

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set the default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
