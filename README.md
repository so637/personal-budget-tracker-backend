# Personal Budget Tracker - Backend 

This is the Django backend for Personal Budget Tracker.

## Features
- User authentication (JWT)
- CRUD for transactions
- CRUD for budgets
- Summary endpoints for dashboard

## Installation
1. Create virtual environment: `python -m venv venv`
2. Activate venv: `venv\Scripts\activate`
3. Install requirements: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`

## API Endpoints
- `/api/transactions/`
- `/api/budgets/`
- `/api/transactions/global-summary/`
- `/api/budgets/global-summary/`
