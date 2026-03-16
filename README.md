# UGC Support System (Helpdesk)

A Django-based ticketing system for managing University departments (IT, Finance, HR, etc.).

## 🚀 Deployment Requirements
To run this project, you must create a `.env` file with the following variables:
* `SECRET_KEY`
* `DEBUG` (set to False for production)
* `DATABASE_URL`
* `EMAIL_USER` & `EMAIL_PASSWORD`

## 🛠️ Installation
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Collect static files: `python manage.py collectstatic`

## 📊 Features
* Automated email notifications to departments.
* Custom Excel/CSV export for support tickets.
* Department-based routing for enquiries.