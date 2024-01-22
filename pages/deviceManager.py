from flask import render_template

from Models.Device import Device
from helpers.mysql import get_device_list_data


class DeviceManager:
    @staticmethod
    def list():
        try:
            devices = []
            for row in get_device_list_data():
                print(row)

                device_info = Device(row)

                print(device_info)
                devices.append(device_info.to_array())

            return render_template('deviceManager.html', devices=devices)

        except Exception as e:
            print('Error:', e)
            return 'An error occurred while fetching data from the database'
