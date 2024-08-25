# Alarm Notification System
## Overview
The Alarm Notification System is a FastAPI-based application that allows users to schedule notifications (or "alarms") at specified times of day. Users can configure the notifications to be sent via email, SMS, or both, on specific days of the week. The system leverages AWS services (SNS, SQS, DynamoDB), Celery for background processing, and PostgreSQL for data storage.

## Features
- User-Configurable Notifications: Users can set multiple alarms with specific times, days, and notification methods (email, SMS, or both).
- Time-Zone Support: Notifications are sent according to the user's time zone.
- Scheduled Notifications: Notifications are processed using Celery and scheduled with APScheduler.
- AWS Integration: Uses AWS SNS for sending notifications and DynamoDB for logging.
- Dockerized: The application is fully containerized using Docker.

## Setup and Installation
### Prerequisites
Ensure you have the following installed:

- Python 3.8+
- Docker
- Docker Compose
- AWS CLI (configured with the correct credentials)

### Clone the Repository
```bash
git clone https://github.com/yourusername/alarm_notification_system.git
cd alarm_notification_system
```

### Setup Virtual Environment
Create and activate a Python virtual environment:

For linux based systems:
```bash
python -m venv venv
source venv/bin/activate
```

Or for windows:
```bash
python -m venv venv
venv/Scripts/activate
```

### Install Dependencies
Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Running the Application
### Running Locally
You can run the FastAPI application locally using Uvicorn:

```bash
uvicorn app.main:app --reload
```

### Running with Docker
Build and run the application using Docker Compose:

```bash
docker-compose up --build
```

This will start the FastAPI application, PostgreSQL, and Celery worker in separate containers.

## Database Migrations
To create and apply database migrations:

### Create a Migration Script:
```bash
alembic revision --autogenerate -m "Initial migration"
```

### Apply the Migration:
```bash
alembic upgrade head
```

## Environment Variables
Your .env file should contain the following environment variables:

```plaintext
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=us-east-1
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
POSTGRES_USER=your-db-user
POSTGRES_PASSWORD=your-db-password
POSTGRES_DB=your-db-name
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

## Docker Setup
### Build and Run the Docker Containers
To build and run the Docker containers:

```bash
docker-compose up --build
```

This will:
- Build the Docker image for the FastAPI application.
- Set up the PostgreSQL database container.
- Start the Celery worker for background processing.

### Accessing the Application
Once the Docker containers are running, you can access the FastAPI application at:

- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc Documentation: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## AWS Configuration
Ensure that your AWS credentials are set up correctly in the .env file and that your AWS CLI is configured with:

```bash
aws configure
```

This project uses AWS SNS for sending notifications and DynamoDB for logging.

## Usage
### API Endpoints
Here are some example API endpoints:
- Create an Alarm: POST /alarms/
- Get All Alarms: GET /alarms/
- Update an Alarm: PUT /alarms/{alarm_id}
- Delete an Alarm: DELETE /alarms/{alarm_id}

### Scheduling and Notifications
- The system checks and schedules alarms every night at midnight.
- Celery workers poll the SQS queue for events and trigger notifications using SNS based on the user's configuration.