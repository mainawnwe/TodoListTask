# Updated to import from celery.py instead of todo/celery.py to avoid circular import

# Fix import to avoid circular import error by importing from celery.py at project root

from celery_app import app as celery_app

__all__ = ('celery_app',)
