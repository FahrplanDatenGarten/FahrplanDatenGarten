# FahrplanDatenGarten

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

## Import Stations from DB
```
python manage.py dbhafas_importstations
```
