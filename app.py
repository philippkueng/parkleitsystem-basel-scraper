import os
from flask import Flask
from flask.ext.heroku import Heroku
import gdata.spreadsheet.service
import gdata.service
import gdata.spreadsheet
import urllib3
import lxml.html
from datetime import datetime

app = Flask(__name__)
heroku = Heroku(app)

app.config['DEBUG'] = os.environ.get('DEBUG')

@app.route('/')
def root():
    return 'Welcome to the Parkleitsytem Basel Scraper'


@app.route('/scrape')
def scrape():
    app.logger.info('start processing...')
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    # fetch the html document from the remote website
    http = urllib3.PoolManager()
    r = http.request('GET', 'http://www.parkleitsystem-basel.ch/stadtplan.php')
    if r.status == 200: # response was correct, continue with the parsing process

        app.logger.info('fetched html successfully, parsing now...')
        
        # parse the html response
        root = lxml.html.fromstring(r.data)

        # collect measurements
        lots = []

        # go through the document and extract each parking name and available lot count
        for tr in root.cssselect("table[summary='Parkhaus DATEN']>tr[class='boxstatustr']"):
            parkingarea_name = tr.cssselect('td>a')[0].text
            parkingarea_lots = tr.cssselect('td>b')[0].text
            lots.append(parkingarea_lots)
            app.logger.info(parkingarea_name + ' has ' + parkingarea_lots + ' available at lots ' + timestamp_str)


        # Create a client class which will make HTTP requests with Google Spreadsheets server.
        client = gdata.spreadsheet.service.SpreadsheetsService()
        # Authenticate using your Google Docs email address and password.
        client.email = os.environ.get('USERNAME')
        client.password = os.environ.get('PASSWORD')
        client.source = 'Parkleitsytem Basel Scraper'
        client.ProgrammaticLogin()

        entry_line = {}
        entry_line['timestamp'] = timestamp_str

        # insert the data into the Google Spreadsheet
        entry = client.InsertRow(entry_line, os.environ.get('SPREADSHEET_KEY'), os.environ.get('WORKSHEET_ID'))
        if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
            app.logger.info('entry succeeeded')
        else:
            app.logger.info('entry failed')


    else: # response was invalid, the site might be down or there's a network error
        # go check again! // TODO
        app.logger.info('the site might be down, check again in a couple of minutes')
        app.logger.error('http status code: ' + r.status)



    return "Website scraped on " + timestamp_str

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)