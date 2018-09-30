###################################################################################
# #Climate App
#Now that you have completed your initial analysis, design a Flask API based on the queries that you have just developed.

#Use FLASK to create your routes.
#################################################################################
#################################################################################
##IMPORT
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, render_template, url_for
from flask_migrate import migrate
import datetime
from sqlalchemy.sql.expression import func
from dateutil import relativedelta

#### Set base directory ####################################
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+ os.path.join(basedir, 'Resources\hawaii.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#################################################
# Database Setup
#################################################
db = SQLAlchemy(app)

db.Model.metadata.reflect(bind=db.engine)

#######################################################
class Hawaii(db.Model):
    __tablename__ = 'measurement'

#    def __init__(self):

    def __repr__(self):
        return "Station {}, Date {}, Percipitation {},  Temperature {}".format(self.station, self.date, self.prcp, self.tobs)

    @staticmethod
    def calc_temps(start_date, end_date):
        """TMIN, TAVG, and TMAX for a list of dates.

        Args:
            start_date (string): A date string in the format %Y-%m-%d
            end_date (string): A date string in the format %Y-%m-%d

            Returns:
            TMIN, TAVE, and TMAX
        """

        return db.session.query(func.min(Hawaii.tobs), func.avg(Hawaii.tobs), func.max(Hawaii.tobs)).\
            filter(Hawaii.date >= start_date).filter(Hawaii.date <= end_date).all()

################################################################################
## HOME PAGE
################################################################################
@app.route('/')
def index():
    return render_template('home.html')

################################################################################
## List all  the data
################################################################################
@app.route('/api/v1.0/all')
def list_data():
    list_data = Hawaii.query.all()
    return render_template('all.html', list_data= list_data)

################################################################################
#/api/v1.0/precipitation
#Convert the query results to a Dictionary using date as the key and tobs as the value.
#Return the JSON representation of your dictionary.
################################################################################
@app.route('/api/v1.0/precipitation')
def precipitation():
    rows = db.session.query(Hawaii.date, Hawaii.prcp).order_by(Hawaii.date.desc())
    temp_dict = {}
    for row in rows:
        temp_dict[row.date] =  row.prcp
    return render_template('precipitation.html', temp_dict= temp_dict)

################################################################################
## Return a JSON list of stations from the dataset.
################################################################################
@app.route('/api/v1.0/stations')
def stations():
    station_data = Hawaii.query.group_by(Hawaii.station).order_by(Hawaii.station)
    return render_template('station.html', station_data= station_data)

################################################################################
#/api/v1.0/tobs

#query for the dates and temperature observations from a year from the last data point.
#Return a JSON list of Temperature Observations (tobs) for the previous year.
################################################################################
@app.route('/api/v1.0/tobs')
def temperature():
    #Get the max date from the table
    #max_date = Hawaii.query.order_by(desc(Hawaii.date))
    max_date= db.session.query(Hawaii.date).order_by(Hawaii.date.desc()).first()
    twelve_months_ago = (datetime.datetime.strptime(max_date[0], '%Y-%m-%d').date() - relativedelta.relativedelta(months=12)).strftime('%Y-%m-%d')
    temp_data = db.session.query(Hawaii).filter(Hawaii.date >= twelve_months_ago)

    return render_template('Temperature.html', temp_data= temp_data)

################################################################################
#/api/v1.0/<start> and /api/v1.0/<start>/<end>

#Return a JSON list of the minimum temperature, the average temperature,
#and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater
#than and equal to the start date. When given the start and the end date,
# calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
################################################################################
@app.route('/api/v1.0/<start>/<end>')
@app.route('/api/v1.0/<start>')
def startenddate(start, end=""):
    dbenddate = datetime.datetime.strptime(db.session.query(Hawaii.date).order_by(Hawaii.date.desc()).first()[0], '%Y-%m-%d').date()
    try:
        startdate = datetime.datetime.strptime(start, '%Y-%m-%d').date()
        if end != "":
            enddate = datetime.datetime.strptime(end, '%Y-%m-%d').date()
        else:
            enddate = dbenddate
    except:
        return render_template('error.html', err="Please enter the Start Date and/or End date in yyyy-mm-dd format")

    if startdate > dbenddate:
        return render_template('error.html', err="Available data is only till {}".format(dbenddate))
    if startdate > enddate:
        return render_template('error.html', err="Start date cannot be greater then end date")

    result = Hawaii.calc_temps(startdate.strftime('%Y-%m-%d'), enddate.strftime('%Y-%m-%d'))
    return render_template('startenddate.html', startdate= startdate, enddate=enddate, result=result)


################################################################################
################################################################################
if __name__ == '__main__':
    app.run(debug=True)
