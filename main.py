import psycopg2
from flask import Flask, render_template, request

# Connect to the PostgreSQL database with the given credentials
conn = psycopg2.connect(
    host="ec2-54-208-11-146.compute-1.amazonaws.com",
    database="d2e1813j7s6m22",
    user="dyykwzvqruluwp",
    password="f69ea4e2f8e25587cc2a705820b76196f5a7790d5551af9ac4e79b81789a162e",
    port="5432"
)

# Dictionary to store the data for each device
device_data = {}

app = Flask(__name__)

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/<device_id>')
def show_data(device_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM device_data WHERE device_id = %s", (device_id,))
    data = cur.fetchall()
    cur.close()
    if not data:
        return 'No data available for device ' + device_id
    else:
        return render_template('data.html', data=data, device_id=device_id)


@app.route('/', methods=['POST'])
def receive_data():
    cur = conn.cursor()
    data_str = request.data.decode('utf-8')
    data_list = data_str.strip().split('\n')
    for data in data_list:
        device_id, co2, air_temp, air_humid, leftwatertemp, rightwatertemp,leftheatertemp, rightheatertemp, leftheaterpwm, rightheaterpwm ,led = data.split()
        # Insert the data into the database
        cur.execute("INSERT INTO device_data (device_id, co2, airtemp, airhumid, leftwatertemp, rightwatertemp, leftheatertemp, rightheatertemp, leftheaterpwm, rightheaterpwm, led) VALUES (%i, %f, %f, %f, %f, %f, %f, %f, %i, %i, %i)", (device_id, co2, air_temp, air_humid, leftwatertemp, rightwatertemp,leftheatertemp, rightheatertemp, leftheaterpwm, rightheaterpwm, led))
    conn.commit()
    cur.close()
    return 'Data received and saved successfully'

if __name__ == '__main__':
    app.run(debug=True)