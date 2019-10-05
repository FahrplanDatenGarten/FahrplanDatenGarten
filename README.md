# FahrplanDatenGarten

## What is it?

A program which save the delay from the trains in a database and you can get the statistics from the frontend.

## Set up the VEnv:
```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
## Set up the database:
Change the `DATABASE_URL` in `.env` basend on the `.env.example` and https://github.com/jacobian/dj-database-url.
Now run
```
source .env
python manage.py migrate
```
