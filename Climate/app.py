import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
import re
from sqlalchemy.sql import exists  


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

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

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query Measurement
    results = (session.query(Measurement.date, Measurement.tobs)
                      .order_by(Measurement.date))
    
    # Create a dictionary
    precipitation_date_tobs = []
    for each_row in results:
        dt_dict = {}
        dt_dict["date"] = each_row.date
        dt_dict["tobs"] = each_row.tobs
        precipitation_date_tobs.append(dt_dict)

    return jsonify(precipitation_date_tobs)


@app.route("/api/v1.0/stations")
def stations():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query Stations
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    station_details = list(np.ravel(results))

    return jsonify(station_details)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
   
    results = session.query(Measurement.tobs, Measurement.date)\
                    .filter(Measurement.date > '2016-08-23')\
                    .order_by(Measurement.date).all()
    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    tobs_list = []
    for result in results:
        row = {}
        row["date"] = result[0]
        row["tobs"] = float(result[1])
        tobs_list.append(row)
    
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start_only(start):

    # Create session (link) from Python to the DB
    session = Session(engine)

    # Date Range (only for help to user in case date gets entered wrong)
    date_range_max = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_range_max_str = str(date_range_max)
    date_range_max_str = re.sub("'|,", "",date_range_max_str)
    print (date_range_max_str)

    date_range_min = session.query(Measurement.date).first()
    date_range_min_str = str(date_range_min)
    date_range_min_str = re.sub("'|,", "",date_range_min_str)
    print (date_range_min_str)


    # Check for valid entry of start date
    valid_entry = session.query(exists().where(Measurement.date == start)).scalar()
 
    if valid_entry:

        results = (session.query(func.min(Measurement.tobs)
                                 ,func.avg(Measurement.tobs)
                                 ,func.max(Measurement.tobs))
                                 .filter(Measurement.date >= start).all())

        tmin =results[0][0]        
        tavg ='{0:.4}'.format(results[0][1])
        tmax =results[0][2]


        result_printout =( ['Entered Start Date: ' + start,
    						'The lowest Temperature was: '  + str(tmin) + ' F',
    						'The average Temperature was: ' + str(tavg) + ' F',
    						'The highest Temperature was: ' + str(tmax) + ' F'])
        

        return jsonify(result_printout)    	

    return jsonify({"error": f"Input Date {start} not valid. Date Range is {date_range_min_str} to {date_range_max_str}"}), 404
   


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    # Create session (link) from Python to the DB
    session = Session(engine)

    # Date Range (only for help to user in case date gets entered wrong)
    date_range_max = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_range_max_str = str(date_range_max)
    date_range_max_str = re.sub("'|,", "",date_range_max_str)
    print (date_range_max_str)

    date_range_min = session.query(Measurement.date).first()
    date_range_min_str = str(date_range_min)
    date_range_min_str = re.sub("'|,", "",date_range_min_str)
    print (date_range_min_str)

    # Check for valid entry of start date
    valid_entry_start = session.query(exists().where(Measurement.date == start)).scalar()
 	
 	# Check for valid entry of end date
    valid_entry_end = session.query(exists().where(Measurement.date == end)).scalar()

    if valid_entry_start and valid_entry_end:

        results = (session.query(func.min(Measurement.tobs)
    				 ,func.avg(Measurement.tobs)
    				 ,func.max(Measurement.tobs))
    					  .filter(Measurement.date >= start)
    				  	  .filter(Measurement.date <= end).all())
        
        tmin =results[0][0]
        tavg ='{0:.4}'.format(results[0][1])
        tmax =results[0][2]

        result_printout =( ['Entered Start Date: ' + start,
    						'Entered End Date: ' + end,
    						'The lowest Temperature was: '  + str(tmin) + ' F',
    						'The average Temperature was: ' + str(tavg) + ' F',
    						'The highest Temperature was: ' + str(tmax) + ' F'])
        
        return jsonify(result_printout)
    
    
    if not valid_entry_start and not valid_entry_end:
        return jsonify({"error": f"Input Start {start} and End Date {end} not valid. Date Range is {date_range_min_str} to {date_range_max_str}"}), 404

    if not valid_entry_end:
         return jsonify({"error": f"Input End Date {end} not valid. Date Range is {date_range_min_str} to {date_range_max_str}"}), 404

    if not valid_entry_start:
    	return jsonify({"error": f"Input Start Date {start} not valid. Date Range is {date_range_min_str} to {date_range_max_str}"}), 404
    
    

if __name__ == '__main__':
    app.run(debug=True)