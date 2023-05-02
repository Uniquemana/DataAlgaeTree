from flask import Flask, render_template, request
from matplotlib import figure
import plotly.graph_objs as go
import plotly.offline as pyo
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Connect to Google Sheets
scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("dataalgaetreegsheets-388ac829236c.json", scope)
client = gspread.authorize(credentials)
sheet = client.open("DATq1").sheet1

app = Flask(__name__)

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/<device_id>')
def show_data(device_id):
    if device_id == 'favicon.ico':
        return ''
    
    # Fetch data from Google Sheets
    data = sheet.get_all_records()

    # Convert device_id to integer
    device_id = int(device_id)

    # Filter data based on the device_id
    filtered_data = [row for row in data if row['device_id'] == device_id]
    
    if len(filtered_data) == 0:
        return 'No data available for device ' + device_id
    else:
        co2_data = [d['co2'] for d in filtered_data]

        # Plotting code without timestamps
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=co2_data, mode='lines', name='CO2 Data', line=dict(color='#aff84e', width=2)))

        # Rest of the plotting code remains the same

        graph_html = pyo.plot(fig, output_type='div')
        return render_template('data.html', data=filtered_data, device_id=device_id, graph_html=graph_html)


@app.route('/', methods=['POST'])
def receive_data():
    data_str = request.data.decode('utf-8')
    data_list = data_str.strip().split('\n')
    try:
        for data in data_list:
            device_id, co2, air_temp, air_humid, leftwatertemp, rightwatertemp, leftheatertemp, rightheatertemp, leftheaterpwm, rightheaterpwm, led = data.strip().split('\t')
            # Append the data to the Google Sheet
            sheet.append_row([device_id, co2, air_temp, air_humid, leftwatertemp, rightwatertemp, leftheatertemp, rightheatertemp, leftheaterpwm, rightheaterpwm, led])
        return 'Data received successfully'
    except Exception as e:
        print('Error:', e)
        return 'An error occurred while inserting data into the database'

if __name__ == '__main__':
    app.run(debug=True)
