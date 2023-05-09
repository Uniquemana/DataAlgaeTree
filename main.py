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
    
    # Fetch data from Google Sheets including header
    data = sheet.get_all_values()

    # Convert device_id to integer
    device_id = int(device_id)

    # Get header row
    header = data[0]

    # Find the last row with the matching device_id
    last_row = None
    filtered_data = []
    for row in data[1:]:  # Exclude the header
        if float(row[0]) == device_id:
            last_row = dict(zip(header, row))
            filtered_data.append(last_row)

    if last_row is None:
        return render_template('no_data.html', device_id=device_id)
    else:
        co2_data = [float(d['co2']) for d in filtered_data]

        # Plotting code without timestamps
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=co2_data, mode='lines', name='CO2 Data', line=dict(color='#aff84e', width=2)))

        # Rest of the plotting code remains the same

        graph_html = pyo.plot(fig, output_type='div')
        return render_template('data.html', data=[last_row], device_id=device_id, graph_html=graph_html)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print('Request headers:', request.headers)
        data_str = request.get_data().decode('utf-8')  # Change this line
        print('Received data:', data_str)
        print('Length of received data:', len(data_str))
        data_list = data_str.strip().split('\n')
        try:
            for data in data_list:
                device_id, co2, air_temp, air_humid, leftwatertemp, rightwatertemp, leftheatertemp, rightheatertemp, leftheaterpwm, rightheaterpwm, led = data.strip().split('\t')
                print('Appending row:', [device_id, co2, air_temp, air_humid, leftwatertemp, rightwatertemp, leftheatertemp, rightheatertemp, leftheaterpwm, rightheaterpwm, led])  # Print the data row to be appended
                # Append the data to the Google Sheet
                response = sheet.append_row([device_id, co2, air_temp, air_humid, leftwatertemp, rightwatertemp, leftheatertemp, rightheatertemp, leftheaterpwm, rightheaterpwm, led])
                print('Response from append_row:', response)
            return 'Data received successfully'
        except Exception as e:
            print('Error:', e)
            return 'An error occurred while inserting data into the database'
    else:
        return render_template('scan.html')

@app.route('/<path:path>')
def catch_all(path):
    return render_template('oops.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
