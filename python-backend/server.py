import os
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_cors import CORS
import oracledb
from config import OracleConfig

# returns cursor
def init_session(connection):
    cursor = oracledb.Cursor(connection)
    cursor.execute("""
        ALTER SESSION SET
            TIME_ZONE = 'UTC'
            NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI'""")
    return cursor

# ends cursor and connection
def end_connection(connection, cursor):
    cursor.close()
    connection.close()

# start_pool(): starts the connection pool
def start_pool(db):

    pool_min = 4
    pool_max = 4
    pool_inc = 0
    pool_gmd = oracledb.SPOOL_ATTRVAL_WAIT

    dsn_tns = db.makedsn()

    print("Connecting to", os.environ.get(dsn_tns))

    pool = oracledb.create_pool(user=os.environ.get(db.username),
                                password=os.environ.get(db.password),
                                dsn=os.environ.get(dsn_tns),
                                min=pool_min,
                                max=pool_max,
                                increment=pool_inc,
                                threaded=True,
                                getmode=pool_gmd,
                                sessionCallback=init_session)

    return pool

app = Flask(__name__)
CORS(app)

# config database instance
db = OracleConfig()
db.init_oracle_client()
dsn = db.makedsn()

# login to database
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db.username = request.form['username']
        db.password = request.form['password']
        return redirect(url_for('dashboard'))
    return render_template('login.html')

# hosts button to aiport view
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Members API Route
@app.route('/members')
def members():
    return ({'members': ['member1', 'member2', 'member3']})

# currently functional
def execute_query(username, password, dsn_tns):
    # Connect to the Oracle database
    connection = oracledb.connect(user=username, password=password, dsn=dsn_tns)
    cursor = init_session(connection)
    cursor.execute('SELECT * FROM AIRPORT')
    rows = cursor.fetchall()
    end_connection(connection, cursor)
    return rows


# if query parameter is given string query, we could use this function for
# every query we need. This could get hard to read and clunky though with long queries.
def test_execute_query(username, password, dsn_tns, query):
    # Connect to the Oracle database
    connection = oracledb.connect(user=username, password=password, dsn=dsn_tns)
    cursor = init_session(connection)
    cursor.execute(query)
    rows = cursor.fetchall()
    end_connection(connection, cursor)
    return rows


# Route to display the results in the browser
@app.route('/display_results')
def display_results():
    # Call the execute_query function to get the results
    results = execute_query(db.username, db.password, dsn)

    # Render a template with the results
    return render_template('results.html', results=results)


if __name__ == "__main__":
    app.run(debug=True)

