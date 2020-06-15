"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq

api = openaq.OpenAQ()

APP = Flask(__name__)
status, body = api.measurements(city='Los Angeles', parameter='pm25')

def parse(body):
    results = body['results']
    utc_times = []
    measurements = []
    for result in results:
        utc_time = result['date']['utc']
        utc_times.append(utc_time)
        measurement = result['value']
        measurements.append(measurement)
    return tuple(zip(utc_times, measurements))

data = parse(body)

@APP.route('/')
def root():
    return str(Record.query.filter(Record.value >= 10).all()) #str(data)


APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        #return f"<Record {self.datetime} {self.value}>"
        return 'Record(datetime=%s, value=%s)' % (self.datetime, self.value)

@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    for element in data:
        new_record = Record(datetime=element[0], value=element[1])
        print(new_record)
        DB.session.add(new_record)
        DB.session.commit()
    return 'Data refreshed!'