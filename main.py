import math

from flask import Flask, render_template, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

from helpers.mysql import insert_device_data
from pages.deviceManager import DeviceManager

# Connect to Google Sheets
scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("dataalgaetreegsheets-388ac829236c.json", scope)
client = gspread.authorize(credentials)
spreadsheet = client.open("DATq1")

app = Flask(__name__)


@app.route('/scan')
def scan():
    return render_template('scan.html')


# Device Manager
@app.route('/')
def device_manager():
    return DeviceManager.list()


# Device data
@app.route('/<deviceID>')
def show_data(deviceID):
    return DeviceManager.get(deviceID)


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
            if not is_valid_float(left_water_temp, min_val=-127, max_val=100):
                print("Invalid left_water_temp")
                return "Invalid data: Invalid left_water_temp"

            # Validate right_water_temp
            right_water_temp = float(data['right_water_temp'])
            if not is_valid_float(right_water_temp, min_val=-127, max_val=100):
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
            response = worksheet.append_row(
                [deviceID, co2, air_temp, air_humid, left_water_temp, right_water_temp, tower_led_pwm, timestamp])
            print('Response from append_row:', response)

            insert_device_data(
                deviceID,
                co2,
                air_temp,
                air_humid,
                left_water_temp,
                right_water_temp,
                tower_led_pwm,
                timestamp,
            )

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
