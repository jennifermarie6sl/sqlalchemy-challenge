from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

### Home Page ###
@app.route("/")
def welcome():
    # """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/yyyy-mm-dd/yyyy-mm-dd"
    )

### precipitation Page ###
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a list"""
    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # # Create a dictionary from the row data and append to a list of percipitations
    precipitation = {date: prcp for date, prcp in results}
    return jsonify(precipitation)

### Stations Page ###
@app.route("/api/v1.0/stations")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

### TOBS Page ###    
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= query_date).all()
    
    session.close()
    
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))

    return jsonify(temperatures=temps)


### Start Page ###
@app.route("/api/v1.0/temp/<startdate>")
def stats_start(startdate=None):
    session = Session(engine)
    # Return TMIN, TAVG, TMAX
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= startdate).all()
    
    session.close()

    # Unravel results into a 1D array and convert to a list
    start_temps = list(np.ravel(results))

    return jsonify(starting_temps=start_temps)


### Start and End Page ###
@app.route("/api/v1.0/temp/<startdate>/<enddate>")
def stats_start_end(startdate=None, enddate=None):
    session = Session(engine)
    # Return TMIN, TAVG, TMAX
    # Select statement
    sql = [func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)]
        # Calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sql).\
        filter(Measurement.date >= startdate).\
        filter(Measurement.date <= enddate).all()  
    
    session.close()

    # Unravel results into a 1D array and convert to a list
    s_e_temps = list(np.ravel(results))

    return jsonify(starting_and_ending_temps=s_e_temps)

if __name__ == '__main__': 
    app.run(debug=True)


    