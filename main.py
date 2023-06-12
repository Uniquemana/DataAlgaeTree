from flask import Flask, render_template, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

# Connect to Google Sheets
scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("dataalgaetreegsheets-388ac829236c.json", scope)
client = gspread.authorize(credentials)
sheet = client.open("DATq1").sheet1

app = Flask(__name__)

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/<deviceID>')
def show_data(deviceID):
    if deviceID == 'favicon.ico':
        return ''

    # Fetch data from Google Sheets including header
    data = sheet.get_all_values()

    # Get header row
    header = data[0]

    # Find the rows with the matching deviceID
    filtered_data = []
    for row in data[1:]:
        if row[0] == deviceID:  # Compare the first column as strings
            filtered_data.append(dict(zip(header, row)))

    if not filtered_data:
        return render_template('no_data.html', deviceID=deviceID)
    else:
        # Extract relevant data fields for display
        device_info = {
            'deviceID': [row['deviceID'] for row in filtered_data],
            'CO2': [float(row['CO2']) for row in filtered_data],
            'air_temp': [float(row['air_temp']) for row in filtered_data],
            'air_humid': [float(row['air_humid']) for row in filtered_data],
            'left_water_temp': [float(row['left_water_temp']) for row in filtered_data],
            'right_water_temp': [float(row['right_water_temp']) for row in filtered_data],
            'left_heater_temp': [float(row['left_heater_temp']) for row in filtered_data],
            'right_heater_temp': [float(row['right_heater_temp']) for row in filtered_data],
            'left_heater_pwm': [int(row['left_heater_pwm']) for row in filtered_data],
            'right_heater_pwm': [int(row['right_heater_pwm']) for row in filtered_data],
            'tower_led_pwm': [int(row['tower_led_pwm']) for row in filtered_data],
            'timestamp': [datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S') for row in filtered_data]
        }


          # Prepare the data for Chart.js
        labels = [timestamp.strftime('%m-%d %H:%M') for timestamp in device_info['timestamp']]
        co2_values = device_info['CO2']

        # Render the data as JSON
        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'CO2 Data',
                    'data': co2_values,
                    'backgroundColor': 'rgba(175, 248, 78, 0.5)',
                    'borderColor': 'rgba(175, 248, 78, 1)',
                    'borderWidth': 2
                }
            ]
        }

        # Convert the chart data to JSON format with proper escaping
        co2_values = device_info['CO2']
        print("CO2 values:", co2_values)
        chart_json = json.dumps(chart_data, indent=None)
        return render_template('data.html', device_info=device_info, deviceID=deviceID, chart_json=chart_json)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.headers.get('Content-Type') == 'application/json':
        try:
            data = request.get_json()

            deviceID = float(data['deviceID'])
            co2 = float(data['CO2'])
            air_temp = float(data['air_temp'])
            air_humid = float(data['air_humid'])
            left_water_temp = float(data['left_water_temp'])
            right_water_temp = float(data['right_water_temp'])
            left_heater_temp = float(data['left_heater_temp'])
            right_heater_temp = float(data['right_heater_temp'])
            left_heater_pwm = int(data['left_heater_pwm'])
            right_heater_pwm = int(data['right_heater_pwm'])
            tower_led_pwm = int(data['tower_led_pwm'])
            year = int(data['time']['year'])
            month = int(data['time']['month'])
            day = int(data['time']['day'])
            hour = int(data['time']['hour'])
            minute = int(data['time']['minute'])
            second = int(data['time']['second'])

            timestamp = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

            # Append the data to the Google Sheet
            response = sheet.append_row([deviceID, co2, air_temp, air_humid, left_water_temp, right_water_temp, left_heater_temp, right_heater_temp, left_heater_pwm, right_heater_pwm, tower_led_pwm, timestamp])
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
