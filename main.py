import psycopg2
from flask import Flask, render_template, request
import plotly.graph_objs as go
import plotly.offline as pyo
import io
import base64

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
    if device_id == 'favicon.ico':
        return ''
    cur = conn.cursor()
    cur.execute("SELECT timestamp, co2, airtemp, airhumid FROM device_data WHERE device_id=%s ORDER BY timestamp DESC", (device_id,))
    data = cur.fetchall()
    if len(data) == 0:
        return 'No data available for device ' + device_id
    else:
        timestamps = [d[0] for d in data]
        co2_data = [d[1] for d in data]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=timestamps, y=co2_data, mode='lines', name='CO2 Data', line=dict(color='#aff84e', width=2)))
        fig.update_layout(
        xaxis_title_font=dict(size=18, color='rgb(255, 255, 255)'),
        yaxis_title_font=dict(size=18, color='rgb(255, 255, 255)'),
        xaxis_color='white',
        yaxis_color='white',
        plot_bgcolor='rgba(104, 101, 111, 0)',
        paper_bgcolor='rgba(104, 101, 111, 0)',
        autosize=True,
        legend=dict(
            x=0,  
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
        )
        )       
        
        graph_html = pyo.plot(fig, output_type='div')
        return render_template('data.html', data=data, device_id=device_id, graph_html=graph_html)




@app.route('/', methods=['POST'])
def receive_data():
    cur = conn.cursor()
    data_str = request.data.decode('utf-8')
    data_list = data_str.strip().split('\n')
    try:
        for data in data_list:
            device_id, co2, air_temp, air_humid, leftwatertemp, rightwatertemp, leftheatertemp, rightheatertemp, leftheaterpwm, rightheaterpwm, led = data.strip().split('\t')
            # Insert the data into the database
            cur.execute("INSERT INTO device_data (device_id, co2, airtemp, airhumid, leftwatertemp, rightwatertemp, leftheatertemp, rightheatertemp, leftheaterpwm, rightheaterpwm, led) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (device_id, co2, air_temp, air_humid, leftwatertemp, rightwatertemp, leftheatertemp, rightheatertemp, leftheaterpwm, rightheaterpwm, led))
        conn.commit()
        return 'Data received successfully'
    except Exception as e:
        print('Error:', e)
        conn.rollback()
        return 'An error occurred while inserting data into the database'
    finally:
        cur.close()