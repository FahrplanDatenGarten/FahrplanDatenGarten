![](https://jhbadge.com/?evt=ber&year=2019)

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

## Themes

There are 4 themes to choose:
* Dark (`@import './styles/dark'`)
* Dark-Mixed (`@import './styles/dark-mixed'`)
* Light (`@import './styles/light'`)
* Light-Mixed (`@import './styles/light-mixed'`)

Change the imports in the `frontend/style.sass` to the new import statements and compile the sass!
