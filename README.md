![](https://jhbadge.com/?evt=ber&year=2019)

# FahrplanDatenGarten
We  ❤️  Deutsche Bahn
## Features
- Daten aus HAFAS in Datenbank speichern
- Fahrgastformular aus Eingaben im Webinterface generieren 
- Statistiken aus Datenbank auswerten

## Contributors
- [N0emis](https://github.com/n0emis)
- [FänselMänsel](https://github.com/fanselMansel)
- [CodeDoctorDE](https://github.com/CodeDoctorDE) / [Gitlab](https://gitlab.com/CodeDoctorDE)
- [Anna](https://github.com/maedchenkunst2013)
## Used API's
  - HAFAS
# Develeopment Setup



## Set up the VEnv:
```
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

There are four different themes to choose from:
* Dark (`@import './styles/dark'`)
* Dark-Mixed (`@import './styles/dark-mixed'`)
* Light (`@import './styles/light'`)
* Light-Mixed (`@import './styles/light-mixed'`)

Change the imports in the `frontend/style.sass` and compile sass!
