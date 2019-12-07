![](https://i.jhbadge.com/?evt=ber&year=2019) [![](https://i.jhbadge.com/?type=view-presentation&evt=ber&year=2018)](https://media.ccc.de/v/jh19-fahrplandatengarten)

and

![](https://i.jhbadge.com/?evt=ulm&year=2019) [![](https://i.jhbadge.com/?type=view-presentation&evt=ulm&year=2019)](https://media.ccc.de/v/currently-not-published)

# FahrplanDatenGarten
We  ❤️  Deutsche Bahn
## Features
-
-
-

## Contributors
- [n0emis](https://github.com/n0emis)
- [FänselMänsel](https://github.com/fanselMansel)
- [CodeDoctorDE](https://github.com/CodeDoctorDE) / [Gitlab](https://gitlab.com/CodeDoctorDE)
- [Anna](https://github.com/maedchenkunst2013)
- [LabCode](https://github.com/labcode-de)
## Used API's
  - HAFAS
# Develeopment Setup

## Install Debian Requirements
```bash
sudo apt install python3-dev python3-wheel
```
## Set up the VEnv:
```bash
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
python manage.py dbapis_importstations
```

## Import Timetable from DB
```
python manage.py dbapis_timetable {IfOpt}
```

## Start Webserver
```
python manage.py runserver
```
The Webserver now runs under http://127.0.0.1:8000/verspaeti/

## Themes

There are four different themes to choose from:
* Dark (`@import './styles/dark'`)
* Dark-Mixed (`@import './styles/dark-mixed'`)
* Light (`@import './styles/light'`)
* Light-Mixed (`@import './styles/light-mixed'`)

Change the imports in the `frontend/style.sass` and compile sass!
