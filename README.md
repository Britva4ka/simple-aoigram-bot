# Telegram Bot Deployment Guide

## Overview

This repository contains a Telegram bot built using **aiogram 3**, with PostgreSQL as the primary database and Redis for FSM storage. The bot handles feedback, support sessions, moderation tasks, else.

## Requirements

Before deploying, ensure you have the following services installed and configured:

1. **PostgreSQL**: For database storage.
2. **Redis**: For FSM storage (optional, defaults to in-memory storage if not provided).
3. **Python 3.11**: The bot runs on Python 3.11.
4. **Docker** *(optional)*: To containerize the application.

---

## Environment Variables

Create a `.env` file in the project root using the provided `dotenv.example` as a reference. Here’s a breakdown of the necessary environment variables:

```env
BOT_TOKEN=TOKEN  # Your Telegram bot token
ADMINS_ID=123456789:987654321  # Admin user IDs, separated by a colon
MODERATORS_SUPPORT_GROUP_ID=-1001234567890  # Group-forum ID (with topics enabled)
MODERATORS_FEEDBACK_GROUP_ID=-1001234567890  # Regular group ID

POSTGRES_USER=user  # PostgreSQL username
POSTGRES_PASSWORD=password  # PostgreSQL password
POSTGRES_HOST=localhost  # PostgreSQL host
POSTGRES_DATABASE=mydatabase  # PostgreSQL database name
POSTGRES_JOB_STORE=mydatabase_job_store  # PostgreSQL job store database name (for scheduled tasks)

REDIS_URL=redis://localhost:6379  # Redis connection URL (optional)
WEB_APP_URL=https://example.com  # Web app URL 
WEB_APP_NAME=WEB-APP  # Web app name

SENTRY_DSN=https://your-dsn  # Sentry DSN url (optional)
```

---

## Setting Up Locally

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_name>
```

### 2. Set Up PostgreSQL and Redis

- **PostgreSQL:**

  1. Install PostgreSQL if not already installed.
  2. Create a database:

  ```sql
  CREATE DATABASE mydatabase;
  CREATE DATABASE mydatabase_job_store;
  ```

- **Redis:**

  1. Install Redis if needed or use an existing instance.
  2. Make sure the Redis service is running.

### 3. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Apply Database Migrations

```bash
alembic upgrade head
```

### 6. Run the Bot

```bash
python __main__.py
```

---

## Docker Deployment

### 1. Build the Docker Image

```bash
docker build -t telegram-bot .
```

### 2. Run the Container

Ensure PostgreSQL and Redis are accessible from inside the container. Update `.env` accordingly.

```bash
docker run --env-file .env telegram-bot
```

---

## Notes for DevOps

1. **Database Migrations:** The Docker container automatically applies Alembic migrations on startup.
2. **Logging:** Ensure that logs are monitored and consider redirecting them to a file or log management system.
3. **Scaling:** The bot is designed for single-instance deployment. For scaling, consider handling FSM storage and job queues appropriately.
4. **Environment Variables:** Double-check all environment variables, especially for production deployments, to ensure security.

---

## Troubleshooting

- **Database Connection Issues:**

  - Ensure PostgreSQL is running and accessible at the provided host.
  - Check that the database credentials match those in `.env`.

- **Redis Issues:**

  - If Redis isn’t running, either start it or remove the `REDIS_URL` from `.env` to use in-memory storage.

- **Bot Not Responding:**

  - Confirm the bot token is correct.
  - Check the network connectivity for the bot.

---

## Contact

For any issues, please contact the project maintainers or refer to the issue tracker on the repository.

---

Happy deploying! 🚀
