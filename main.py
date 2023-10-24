import math
from flask import Flask, render_template, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import json

# Connect to Google Sheets
scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("dataalgaetreegsheets-388ac829236c.json", scope)
client = gspread.authorize(credentials)
spreadsheet = client.open("DATq1")

app = Flask(__name__)

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/')
def device_manager():
    try:
        # Get the list of sheets in the spreadsheet
        spreadsheet = client.open("DATq1")
        all_sheets = spreadsheet.worksheets()

        # Prepare a list to store data for all devices
        all_devices_data = []

        for sheet in all_sheets:
            # Fetch data from the current sheet
            data = sheet.get_all_values()

            # Get header row
            header = data[0]

            # Prepare the data for each device
            devices = []
            for row in data[1:]:
                device_info = dict(zip(header, row))
                try:
                    device_info['timestamp'] = datetime.strptime(device_info['timestamp'], '%Y-%m-%d %H:%M:%S')
                except ValueError as e:
                    # Log the timestamp that caused the error for debugging purposes
                    print(f"Error parsing timestamp: {device_info['timestamp']}, Error: {e}")
                    # You may also consider setting a default timestamp or skipping the data with an incorrect timestamp
                devices.append(device_info)

            # Filter the devices to get the last data of each device
            last_data_per_device = {}
            for device in devices:
                device_id = device['deviceID']
                if device_id not in last_data_per_device:
                    last_data_per_device[device_id] = device
                elif device['timestamp'] > last_data_per_device[device_id]['timestamp']:
                    last_data_per_device[device_id] = device

            # Round CO2 values for display
            for device in last_data_per_device.values():
                device['CO2'] = round(float(device['CO2']))
                device['air_temp'] = round(float(device['air_temp']))
                device['air_humid'] = round(float(device['air_humid']))

            # Add data for the current sheet (device) to the list
            all_devices_data.extend(last_data_per_device.values())

        return render_template('deviceManager.html', devices=all_devices_data)

    except Exception as e:
        print('Error:', e)
        return 'An error occurred while fetching data from the database'





@app.route('/<deviceID>')
def show_data(deviceID):
    if deviceID == 'favicon.ico':
        return ''

    try:
        # Fetch the sheet corresponding to the deviceID
        spreadsheet = client.open("DATq1")
        worksheet = None

        # Check if the sheet with the given deviceID exists
        try:
            worksheet = spreadsheet.worksheet(deviceID)
        except gspread.exceptions.WorksheetNotFound:
            return render_template('no_data.html', deviceID=deviceID)

        # Fetch data from the selected sheet
        data = worksheet.get_all_values()

        # Get header row
        header = data[0]

        # Currently generating grams of CO2
        grams_co2 = 30

        # Currently collecting in ppm
        collecting_co2_ppm = 347

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
                'CO2': [round(float(row['CO2'])) for row in filtered_data],  # Rounded CO2 value
                'air_temp': [round(float(row['air_temp'])) for row in filtered_data],  # Rounded air_temp value
                'air_humid': [round(float(row['air_humid'])) for row in filtered_data],  # Rounded air_humid value
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
            air_temp_values = device_info['air_temp']
            air_humid_values = device_info['air_humid']
            left_water_temp = device_info['left_water_temp']
            right_water_temp = device_info['right_water_temp']
            tower_led_pwm = device_info['tower_led_pwm']

            # Extract timestamps for counting unique days
            timestamps = device_info['timestamp']

            # Count unique days
            unique_day_count = count_unique_days(timestamps)

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
                    },
                    {
                        'label': 'air_temp',
                        'data': air_temp_values,
                        'backgroundColor': 'rgba(239, 98, 98, 0.5)',
                        'borderColor': 'rgba(239, 98, 98, 1)',
                        'borderWidth': 2
                    },
                    {
                        'label': 'air_humid',
                        'data': air_humid_values,
                        'backgroundColor': 'rgba(239, 98, 98, 0.5)',
                        'borderColor': 'rgba(239, 98, 98, 1)',
                        'borderWidth': 2
                    },
                    {
                        'label': 'left_water_temp',
                        'data': left_water_temp,
                        'backgroundColor': 'rgba(20, 195, 142, 0.5)',
                        'borderColor': 'rgba(20, 195, 142, 1)',
                        'borderWidth': 2
                    },
                    {
                        'label': 'right_water_temp',
                        'data': right_water_temp,
                        'backgroundColor': 'rgba(20, 195, 189, 0.5)',
                        'borderColor': 'rgba(20, 195, 189, 1)',
                        'borderWidth': 2
                    },
                    {
                        'label': 'tower_led_pwm',
                        'data': tower_led_pwm,
                        'backgroundColor': 'rgba(221, 88, 214, 0.5)',
                        'borderColor': 'rgba(221, 88, 214, 1)',
                        'borderWidth': 2
                    }
                ]
            }

            # Convert the chart data to JSON format with proper escaping
            co2_values = device_info['CO2']
            air_temp_values = device_info['air_temp']
            air_humid_values = device_info['air_humid']
            left_water_temp = device_info['left_water_temp']
            right_water_temp = device_info['right_water_temp']
            tower_led_pwm = device_info['tower_led_pwm']

            chart_json = json.dumps(chart_data, indent=None)
            return render_template('data.html', device_info=device_info, deviceID=deviceID, chart_json=chart_json,
                                   collecting_co2_ppm=collecting_co2_ppm, grams_co2=grams_co2,
                                   unique_day_count=unique_day_count)

    except Exception as e:
        print('Error:', e)
        return 'An error occurred while fetching data from the database'

# Function to check if a sheet with the given title exists
def sheet_exists(spreadsheet, title):
    try:
        worksheet = spreadsheet.worksheet(title)
        return True
    except gspread.exceptions.WorksheetNotFound:
        return False

# Function to create a new sheet with the given title
def create_sheet(spreadsheet, title):
    worksheet = spreadsheet.add_worksheet(title, rows=1, cols=1)
    return worksheet.title

# Function to validate if a float value is valid (non-NaN, finite, and within a specific range)
def is_valid_float(value, min_val=None, max_val=None):
    if not isinstance(value, (float, int)) or math.isnan(value) or math.isinf(value):
        return False

    if min_val is not None and value < min_val:
        return False

    if max_val is not None and value > max_val:
        return False

    return True

# Function to validate if an integer value is valid (non-NaN, finite, and within a specific range)
def is_valid_int(value, min_val=None, max_val=None):
    if not isinstance(value, int) or math.isnan(value) or math.isinf(value):
        return False

    if min_val is not None and value < min_val:
        return False

    if max_val is not None and value > max_val:
        return False

    return True

#Counts the active days for the device based on unique day timestamp
def count_unique_days(timestamps):
    unique_days = set()
    for timestamp in timestamps:
        unique_days.add(timestamp.date())
    return len(unique_days)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.headers.get('Content-Type') == 'application/json':
        try:
            data = request.get_json()

            # Validate deviceID
            deviceID = float(data['deviceID'])
            # if not is_valid_float(deviceID, min_val=1000, max_val=1003):
            #     print("Invalid deviceID")
            #     return "Invalid data: Invalid deviceID"

            # Validate CO2
            co2 = float(data['CO2'])
            if not is_valid_float(co2, min_val=250, max_val=15000):
                print("Invalid CO2 value")
                return "Invalid data: Invalid CO2 value"

            # Validate air_temp
            air_temp = float(data['air_temp'])
            if not is_valid_float(air_temp, min_val=-50, max_val=60):
                print("Invalid air_temp")
                return "Invalid data: Invalid air_temp"

            # Validate air_humid
            air_humid = float(data['air_humid'])
            if not is_valid_float(air_humid, min_val=0, max_val=100):
                print("Invalid air_humid")
                return "Invalid data: Invalid air_humid"

            # Validate left_water_temp
            left_water_temp = float(data['left_water_temp'])
            if not is_valid_float(left_water_temp, min_val=-50, max_val=100):
                print("Invalid left_water_temp")
                return "Invalid data: Invalid left_water_temp"

            # Validate right_water_temp
            right_water_temp = float(data['right_water_temp'])
            if not is_valid_float(right_water_temp, min_val=-50, max_val=100):
                print("Invalid right_water_temp")
                return "Invalid data: Invalid right_water_temp"

            # # Validate left_heater_temp
            # left_heater_temp = float(data['left_heater_temp'])
            # if not is_valid_float(left_heater_temp, min_val=-50, max_val=300):
            #     print("Invalid left_heater_temp")
            #     return "Invalid data: Invalid left_heater_temp"

            # # Validate right_heater_temp
            # right_heater_temp = float(data['right_heater_temp'])
            # if not is_valid_float(right_heater_temp, min_val=-50, max_val=300):
            #     print("Invalid right_heater_temp")
            #     return "Invalid data: Invalid right_heater_temp"

            # # Validate left_heater_pwm
            # left_heater_pwm = int(data['left_heater_pwm'])
            # if not is_valid_int(left_heater_pwm, min_val=0, max_val=255):
            #     print("Invalid left_heater_pwm")
            #     return "Invalid data: Invalid left_heater_pwm"

            # # Validate right_heater_pwm
            # right_heater_pwm = int(data['right_heater_pwm'])
            # if not is_valid_int(right_heater_pwm, min_val=0, max_val=255):
            #     print("Invalid right_heater_pwm")
            #     return "Invalid data: Invalid right_heater_pwm"

            # Validate tower_led_pwm
            tower_led_pwm = int(data['tower_led_pwm'])
            if not is_valid_int(tower_led_pwm, min_val=0, max_val=255):
                print("Invalid tower_led_pwm")
                return "Invalid data: Invalid tower_led_pwm"

            year = int(data['time']['year'])
            month = int(data['time']['month'])
            day = int(data['time']['day'])
            hour = int(data['time']['hour'])
            minute = int(data['time']['minute'])
            second = int(data['time']['second'])

            # Validate individual components of the timestamp
            if (
                year < 1970 or year > 2030 or
                month < 1 or month > 12 or
                day < 1 or day > 31 or
                hour < 0 or hour > 23 or
                minute < 0 or minute > 59 or
                second < 0 or second > 59
            ):
                # Handle the error, e.g., log an error message or return a response indicating invalid data
                print("Invalid timestamp components")
                return "Invalid data: Invalid timestamp components"

            # Construct the timestamp string
            timestamp = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

            # Parse the received timestamp and the current UTC timestamp
            received_timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            current_utc_timestamp = datetime.utcnow()

            # Check if the difference between the received timestamp and current UTC timestamp is within 12 hours
            if abs(current_utc_timestamp - received_timestamp) > timedelta(hours=12):
                # Handle the error, e.g., log an error message or return a response indicating invalid data
                print("Timestamp difference exceeds 12 hours")
                return "Invalid data: Timestamp difference exceeds 12 hours"

             # Extracted the sheet ID creation logic to a separate function
            def create_or_get_sheet(spreadsheet, device_id):
                sheet_title = str(int(device_id))
                if not sheet_exists(spreadsheet, sheet_title):
                    return create_sheet(spreadsheet, sheet_title)
                else:
                    return sheet_title

            # Check if the sheet with the device ID exists, create it if not
            sheet_id = create_or_get_sheet(spreadsheet, deviceID)

            # Get the worksheet based on the sheet_id
            worksheet = spreadsheet.worksheet(sheet_id)

            # Append the data to the Google Sheet
            response = worksheet.append_row([deviceID, co2, air_temp, air_humid, left_water_temp, right_water_temp, left_heater_temp, right_heater_temp, left_heater_pwm, right_heater_pwm, tower_led_pwm, timestamp])
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
