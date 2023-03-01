from flask import Flask, request, render_template
import sqlite3
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__, template_folder='templates', static_folder='static')

# Connect to database
conn = sqlite3.connect('/path/to/database.db')
c = conn.cursor()

@app.route('/data', methods=['POST'])
def data():
    # Get POST data
    co2 = request.form.get('co2')
    airTemp = request.form.get('airTemp')
    airHumidity = request.form.get('airHumidity')

    # Insert data into database
    c.execute("INSERT INTO data (co2, airTemp, airHumidity) VALUES (?, ?, ?)", (co2, airTemp, airHumidity))
    conn.commit()

    return 'OK'

@app.route('/latest')
def latest():
    # Get latest data from database
    c.execute("SELECT * FROM data ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    co2 = row[1]
    airTemp = row[2]
    airHumidity = row[3]

    # Render template with latest data
    return render_template('latest.html', co2=co2, airTemp=airTemp, airHumidity=airHumidity)

if __name__ == '__main__':
    app.run(debug=True)