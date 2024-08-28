# Alarm Notification System
## Overview
The Alarm Notification System is a FastAPI-based application that allows users to schedule notifications (or "alarms") at specified times of day. Users can configure the notifications to be sent via email, SMS, or both, on specific days of the week. The system leverages AWS services (SNS, DynamoDB), and PostgreSQL for data storage.

## Features
- User-Configurable Notifications: Users can set multiple alarms with specific times, days, and notification methods (email, SMS, or both).
- Scheduled Notifications: Notifications scheduled with APScheduler.
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
git clone https://github.com/lilvedaes/AlarmNotificationSystem.git
cd AlarmNotificationSystem
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

This will start the FastAPI application, and PostgreSQL in separate containers.

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

## Apply the migration to Docker

In Docker, thanks to the command in the web container, the migrations are applied successfully on start.

## Environment Variables
Your .env file should contain the following environment variables:

```plaintext
DATABASE_URL=postgresql://user:password@host/database
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=database
POSTGRES_HOST=host
POSTGRES_PORT=5432
TIMEZONE=Timezone

AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=your-region
SNS_TOPIC_ARN=arn:aws:sns:your-region:your-account-id:your-topic-name
```

Note:
- DATABASE_URL should NOT be an async url
- The TIMEZONE will define what timezone your app will run in

## Docker Setup
### Build and Run the Docker Containers
To build and run the Docker containers:

```bash
docker-compose up --build
```

This will:
- Build the Docker image for the FastAPI application.
- Set up the PostgreSQL database container.

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
The available API endpoints are:
- Display welcome message: /
- Create user: POST /users/
- Get user by username: GET /users/{username}
- Create alarm: POST /alarms/
- Get alarms by username: GET /alarms/user/{username}
- Delete alarm by alarm ID: DELETE /alarms/{alarm_id}

### Scheduling and Notifications
- We use APSCheduler Job Storage to schedule the alarms when created
- When the alarms are done, we send the SNS notifications