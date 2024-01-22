import json
import os
import sys
from datetime import datetime

from flask import render_template

from Models.Device import Device
from helpers.mysql import get_device_list_data, get_device_data, get_device_chart_data


class DeviceManager:
    @staticmethod
    def list() -> str:
        try:
            devices = []
            for row in get_device_list_data():
                device_info = Device(row)
                devices.append(device_info.to_array())

            return render_template('deviceManager.html', devices=devices)

        except Exception as e:
            print('Error:', e)
            return 'An error occurred while fetching data from the database'

    @staticmethod
    def get(device_id: str) -> str:
        if device_id == 'favicon.ico':
            return ''

        try:
            # Currently generating grams of CO2
            grams_co2 = 30

            # Currently collecting in ppm
            collecting_co2_ppm = 347

            current_device_data = list(get_device_data(device_id))

            # Find the rows with the matching deviceID
            filtered_data = list(get_device_chart_data(device_id))

            print(current_device_data)

            if not current_device_data:
                return render_template('no_data.html', deviceID=device_id)

            # id  co2,          air_temp, air_humid, lwt, rwt,  tlp  timestamp
            # [(1001, 563.5753, 28.76405, 26.71593, 21.0, 22.0, 0.0, datetime.datetime(2023, 11, 15, 21, 9, 27))]

            # Extract relevant data fields for display
            device_info = {
                'deviceID': device_id,
                'CO2': round(current_device_data[1]),  # Rounded CO2 value
                'air_temp': round(current_device_data[2]),  # Rounded air_temp value
                'air_humid': round(current_device_data[3]),  # Rounded air_humid value
                'left_water_temp': round(current_device_data[4]),
                'right_water_temp': round(current_device_data[5]),
                'tower_led_pwm': round(current_device_data[6]),
                'timestamp': current_device_data[7]
            }

            print(filtered_data[0])

            # Prepare the data for Chart.js
            labels = [row[7] for row in filtered_data]
            co2_values = [round(float(row[1])) for row in filtered_data]
            air_temp_values = [round(float(row[2])) for row in filtered_data]
            air_humid_values = [round(float(row[3])) for row in filtered_data]
            left_water_temp = [float(row[4]) for row in filtered_data]
            right_water_temp = [float(row[5]) for row in filtered_data]
            tower_led_pwm = [int(row[6]) for row in filtered_data]

            # Extract timestamps for counting unique days
            timestamps = [row[7] for row in filtered_data]

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

            chart_json = json.dumps(chart_data, indent=None)

            print(device_info)

            return render_template('data.html', device_info=device_info, deviceID=device_id, chart_json=chart_json,
                                   collecting_co2_ppm=collecting_co2_ppm, grams_co2=grams_co2,
                                   unique_day_count=unique_day_count)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)

            return 'An error occurred while fetching data from the database'


# Counts the active days for the device based on unique day timestamp
def count_unique_days(timestamps):
    unique_days = set()
    for timestamp in timestamps:
        date = datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
        unique_days.add(date.date())
    return len(unique_days)
