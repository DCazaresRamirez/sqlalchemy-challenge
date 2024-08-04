# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

#################################################
# Database Setup
#################################################

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# Reflect the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Home route
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session from Python to the DB
    session = Session(engine)

    # Calculate the date one year ago from the most recent date in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    session.close()

    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    # Create session from Python to the DB
    session = Session(engine)

    # Query all stations
    stations_data = session.query(Station.station).all()
    session.close()

    # Convert list of tuples into a normal list
    stations_list = [station[0] for station in stations_data]

    return jsonify(stations_list)

# Temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    # Create session from Python to the DB
    session = Session(engine)

    # Calculate the date one year ago from the most recent date in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the most active station
    most_active_station_id = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    # Query the last 12 months of temperature observation data for the most active station
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Convert the query results to a list of dictionaries
    temperature_list = [{"date": date, "temperature": tobs} for date, tobs in temperature_data]

    return jsonify(temperature_list)

# Temperature statistics route with a start date
@app.route("/api/v1.0/<start>")
def temperature_stats_start(start):
    # Create session from Python to the DB
    session = Session(engine)

    try:
        # Convert start to datetime object
        start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid start date format. Use YYYY-MM-DD."}), 400

    # Query for temperature data
    temperature_data = session.query(
        func.min(Measurement.tobs).label("TMIN"),
        func.max(Measurement.tobs).label("TMAX"),
        func.avg(Measurement.tobs).label("TAVG")
    ).filter(Measurement.date >= start_date).all()

    session.close()

    # Convert the query results to a dictionary
    temperature_stats = {
        "TMIN": temperature_data[0].TMIN,
        "TMAX": temperature_data[0].TMAX,
        "TAVG": temperature_data[0].TAVG
    }

    return jsonify(temperature_stats)

# Route for temperature statistics with a start and end date
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_start_end(start, end):
    # Create session from Python to the DB
    session = Session(engine)

    try:
        # Convert start and end to datetime objects
        start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
        end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # Query for temperature data
    temperature_data = session.query(
        func.min(Measurement.tobs).label("TMIN"),
        func.max(Measurement.tobs).label("TMAX"),
        func.avg(Measurement.tobs).label("TAVG")
    ).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    # Convert the query results to a dictionary
    temperature_stats = {
        "TMIN": temperature_data[0].TMIN,
        "TMAX": temperature_data[0].TMAX,
        "TAVG": temperature_data[0].TAVG
    }

    return jsonify(temperature_stats)

if __name__ == '__main__':
    app.run(debug=True)
