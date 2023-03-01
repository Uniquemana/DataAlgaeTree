from flask import Flask, request, render_template
import sqlite3
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/app')
def atapp():
    co2 = 1037
    airtemp = 21
    airhumid = 35
    return render_template("main.html",co2 = co2, airtemp = airtemp, airhumid = airhumid)


conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS data
             (timestamp DATETIME, co2 INTEGER, airTemp REAL, airHumidity REAL, led REAL)''')
conn.commit()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/data', methods=['POST'])
def receive_data():
    co2 = request.form['co2']
    airTemp = request.form['airTemp']
    airHumidity = request.form['airHumidity']
    led = request.form['led']
    c.execute("INSERT INTO data (timestamp, co2, airTemp, airHumidity, led) VALUES (datetime('now'), ?, ?, ?)",
              (co2, airTemp, airHumidity, led))
    conn.commit()
    return 'Data received'

@app.route('/latest', methods=['GET'])
def latest_data():
    c.execute("SELECT * FROM data ORDER BY timestamp DESC LIMIT 1")
    row = c.fetchone()
    if row:
        co2 = row[1]
        airTemp = row[2]
        airHumidity = row[3]
        led = row[4]
        return render_template('main.html', co2=co2, airTemp=airTemp, airHumidity=airHumidity,led=led)
    else:
        return 'No data'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')