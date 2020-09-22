# FahrplanDatenGarten
![](https://jhbadge.freetls.fastly.net/?evt=ber&year=2019) [![](https://jhbadge.freetls.fastly.net/?type=view-presentation&evt=ber&year=2018)](https://media.ccc.de/v/jh19-fahrplandatengarten)
![](https://jhbadge.freetls.fastly.net/?evt=ulm&year=2019) [![](https://jhbadge.freetls.fastly.net/?type=view-presentation&evt=ulm&year=2019)](https://media.ccc.de/v/currently-not-published)

[![#FahrplanDatenGarten on matrix.org](https://img.shields.io/matrix/fahrplandatengarten:matrix.org?logo=matrix&server_fqdn=matrix.org)](https://riot.im/app/#/room/#fahrplandatengarten:matrix.org)

We  ❤️  Deutsche Bahn

## Used API's
  - HAFAS

# Setup

## Init and Update git-submodules
```
git submodule init
git submodule update
```

## Install Debian Requirements *(only on debian systems)*
```bash
sudo apt install python3-dev python3-wheel python3-venv
```
## Set up the VEnv *(optional, but recommended)*
Using an VEnv will help you to avoid dependency-(version)-conflicts.
```bash
python3 -m venv .venv
source .venv/bin/activate
```
You can deactivate the VEnv, by simply running `deactivate`.
If you want to re-enable the VEnv later, simply run `source .venv/bin/activate` again.

## Install python dependencies
```
pip install -U -r requirements.txt
```

## Set up the database
Copy `.env.example` to `.env` and change the `database` block.
Now run

## Migrate your database
This and all later commands will have to be run from inside the folder `FahrplanDatenGarten`.
```
python manage.py migrate
```

## Import Stations from DB
```
python manage.py dbapis_importstations
```

## Import Timetable from DB *(optional)*
```
python manage.py dbapis_timetable {StationName}
```

## Update Journeys *(optional)*
```
python manage.py dbapis_journey
```

## Start Webserver
```
python manage.py runserver
```
The Webserver now runs under http://127.0.0.1:8000/
