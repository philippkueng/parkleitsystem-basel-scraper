# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import sys
import gdata.spreadsheet.service
import gdata.service
import gdata.spreadsheet
import urllib3
import lxml.html
from datetime import datetime

def scrape():
    sys.stdout.write('start processing...')
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    # fetch the html document from the remote website
    http = urllib3.PoolManager()
    r = http.request('GET', 'http://www.parkleitsystem-basel.ch/stadtplan.php')
    if r.status == 200: # response was correct, continue with the parsing process

        sys.stdout.write('fetched html successfully, parsing now...')
        
        # parse the html response
        root = lxml.html.fromstring(r.data)

        # collect measurements
        lots = []

        # go through the document and extract each parking name and available lot count
        for tr in root.cssselect("table[summary='Parkhaus DATEN']>tr[class='boxstatustr']"):
            parkingarea_name = tr.cssselect('td>a')[0].text
            parkingarea_lots = tr.cssselect('td>b')[0].text
            lots.append(parkingarea_lots)
            sys.stdout.write(parkingarea_name + ' has ' + parkingarea_lots + ' available at lots ' + timestamp_str)


        # Create a client class which will make HTTP requests with Google Spreadsheets server.
        client = gdata.spreadsheet.service.SpreadsheetsService()
        # Authenticate using your Google Docs email address and password.
        client.email = os.environ.get('USERNAME')
        client.password = os.environ.get('PASSWORD')
        client.source = 'Parkleitsytem Basel Scraper'
        client.ProgrammaticLogin()

        entry_line = {}
        entry_line['timestamp'] = timestamp_str
        entry_line['badischerbahnhof'] = lots[0]
        entry_line['messe'] = lots[1]
        entry_line['europe'] = lots[2]
        entry_line['rebgasse'] = lots[3]
        entry_line['claramatte'] = lots[4]
        entry_line['elisabethen'] = lots[5]
        entry_line['steinen'] = lots[6]
        entry_line['city'] = lots[7]
        entry_line['storchen'] = lots[8]
        entry_line['postbasel'] = lots[9]
        entry_line['centralbahnparking'] = lots[10]
        entry_line['hilton'] = lots[11]
        entry_line['aeschen'] = lots[12]
        entry_line['anfos'] = lots[13]
        entry_line['bahnhofsued'] = lots[14]


        # insert the data into the Google Spreadsheet
        entry = client.InsertRow(entry_line, os.environ.get('SPREADSHEET_KEY'), os.environ.get('WORKSHEET_ID'))
        if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
            sys.stdout.write('scraping for ' + timestamp_str + ' was successful.')
        else:
            sys.stdout.write('inserting an entry failed')


    else: # response was invalid, the site might be down or there's a network error
        # go check again! // TODO
        sys.stdout.write('the site might be down, check again in a couple of minutes')
        sys.stdout.write('http status code: ' + r.status)



    return "Website scraped on " + timestamp_str
    
scrape() # execute the scraping process