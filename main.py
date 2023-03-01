from flask import Flask, request, render_template
import sqlite3
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__, template_folder='templates', static_folder='static')

if __name__ == '__main__':
    app.run()


@app.route('/app')
def atapp():
    co2 = 1037
    airtemp = 21
    airhumid = 35
    return render_template("main.html",co2 = co2, airtemp = airtemp, airhumid = airhumid)


@app.route('/dashboard')
def dashboard():
    return render_template("index.html")




@app.route('/data_endpoint', methods=['POST'])
def handle_data():
    # Get the data from the POST request
    data = request.data.decode('utf-8')

    # Parse the data and store it in the database
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS sensor_data (temperature real, co2 real, humidity real)')
    c.execute('INSERT INTO sensor_data VALUES (?, ?, ?)', data.split(','))

    conn.commit()
    conn.close()

    return 'Data received'

@app.route('/plot/<column>')
def plot_data(column):
    # Retrieve the data from the database
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute(f'SELECT {column} FROM sensor_data')
    data = c.fetchall()
    conn.close()

    # Create the plot
    fig, ax = plt.subplots()
    ax.plot(data)

    # Convert the plot to a PNG image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the PNG image as base64
    data_uri = base64.b64encode(buffer.read()).decode('utf-8')

    return f'<img src="data:image/png;base64,{data_uri}"/>'


