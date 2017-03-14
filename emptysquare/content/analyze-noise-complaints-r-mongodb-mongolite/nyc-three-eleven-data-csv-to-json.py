import csv
import datetime
import sys

from bson import json_util  # from PyMongo

date_fmt = '%m/%d/%Y %I:%M:%S %p'
parse_dt = lambda x: datetime.datetime.strptime(x, date_fmt) if x else None
flt = lambda x: float(x) if x else None

for row in csv.DictReader(sys.stdin):
    if row['Longitude'] and row['Latitude']:
        location = {
            'type': 'Point',
            'coordinates': [flt(row['Longitude']), flt(row['Latitude'])]}
    else:
        location = None

    print(json_util.dumps({
        'address': row['Incident Address'],
        'city': row['City'],
        'zip': row['Incident Zip'],
        'agency': row['Agency'],
        'borough': row['Borough'],
        'created': parse_dt(row['Created Date']),
        'closed': parse_dt(row['Closed Date']),
        'complaintType': row['Complaint Type'],
        'descriptor': row['Descriptor'],
        'location': location,
        'resolution': row['Resolution Description'],
        'status': row['Status']
    }, json_options=json_util.STRICT_JSON_OPTIONS))
