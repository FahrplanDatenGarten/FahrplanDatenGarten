![](https://jhbadge.com/?evt=ber&year=2019)

# FahrplanDatenGarten
We  ❤️  Deutsche Bahn
## Features
- Hier könnte ihre Werbung stehen!


## Contributors
- [Simeon/N0emis](https://github.com/marvinborner)
- [Felix](https://github.com/fanselMansel)
- [CodeDoctorDE](https://github.com/CodeDoctorDE) / [Gitlab](https://gitlab.com/CodeDoctorDE)


## Contributing
To contribute to this project create a pull request which will then be merged only by the main [contributors](#contributors) so that we have at least some control over the current version of the code in this master branch

## Additional Links

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
