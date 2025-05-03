# Todo List Task Project

This is a Django-based Todo List application with user authentication, task management, task prioritization, reminders with email notifications, and category filtering.

## Prerequisites

- Python 3.8+
- Redis server (for Celery message broker)
- Virtual environment tool (optional but recommended)

## Setup Instructions

Follow these steps to run the project on your local machine:

### 1. Clone the repository

```bash
git clone <repository-url>
cd TodoListTask-main
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure email settings

Update the email settings in `todo/settings.py` with your SMTP credentials (e.g., Gmail SMTP).

### 5. Run database migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (optional, for admin access)

```bash
python manage.py createsuperuser
```

### 7. Start Redis server

Make sure Redis is installed and running:

```bash
redis-server
```

### 8. Start Celery worker and beat scheduler

Open two separate terminal windows/tabs and run:

```bash
celery -A celery_app worker --loglevel=info
```

```bash
celery -A celery_app beat --loglevel=info
```

### 9. Run the Django development server

```bash
python manage.py runserver
```

### 10. Access the application

Open your browser and go to `http://127.0.0.1:8000/`

## Features

- User registration and login
- Create, update, delete tasks with categories and priorities
- Set reminders for tasks with email notifications
- Filter tasks by category
- Profile management with profile picture and bio

## Notes

- Reminder emails are sent immediately when a task with a reminder is created or updated.
- Periodic reminder emails are also sent by a scheduled Celery task.
- Make sure to keep the Celery worker and beat scheduler running to enable asynchronous task processing.

## Troubleshooting

- If you do not receive reminder emails, verify your email SMTP settings.
- Check that Redis server is running.
- Ensure Celery worker and beat are running alongside the Django server.

## License

This project is for educational purposes.

---

If you have any questions or issues, feel free to contact me.
