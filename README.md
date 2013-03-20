# Parkleitsystem Basel Scraper

## Setup (Development)

1. Install python, pip and virtualenv
2. clone the repository
3. `virtualenv venv --no-site-packages`
4. source venv/bin/activate
5. pip install -r requirements.txt
6. install (foreman)[https://toolbelt.heroku.com/]
7. put an .env file into the root of the folder with all variables filled out
7. foreman start

## Setup (deploy on heroku)

1. heroku create <app-name> --stack cedar
2. heroku config:set USERNAME=<your-gmail-username> PASSWORD=<your-gmail-password> SPREADSHEET_KEY=<the-key> WORKSHEET_ID=<usually-od6>
2. git push heroku master
