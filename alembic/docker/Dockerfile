# alembic/docker/Dockerfile

FROM python:3.8

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the migration code
COPY . .

# Set the entrypoint for running migrations
ENTRYPOINT ["/app/entrypoint.sh"]
