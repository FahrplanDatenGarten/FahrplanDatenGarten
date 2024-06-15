import csv
import io

import requests


def parse_db_opendata_stop_csv():
    # The csv is unavailable. as we already have the required data, we can skip the import
    return []
    r = requests.get(
        'http://download-data.deutschebahn.com/static/datasets/haltestellen/D_Bahnhof_2020_alle.CSV')
    r.encoding = 'utf-8'
    csv_string = r.text
    csv_file = io.StringIO()
    csv_file.write(csv_string)
    csv_file.seek(0)
    return csv.DictReader(csv_file, delimiter=';')
