# DataAlgaeTree

Algae Tree Bioreactor Device Monitoring - IoT Functionality
Welcome to the Algae Tree Bioreactor Device Monitoring project. This is an IoT-based project that allows you to monitor the Algae Tree bioreactor device remotely. The project uses an ESP32 microcontroller to collect data from the device and then sends it to a webserver, where the data is displayed in real-time. The data includes CO2, air temperature, air humidity, and LED light intensity.

Getting Started
To get started with the project, you will need the following:

1. An Algae Tree bioreactor device
2. An ESP32 microcontroller
3. A webserver to display the data

Installation:

1. Clone the project repository to your local machine using the following command:
```
git clone https://github.com/Uniquemana/DataAlgaeTree.git
```

2. Install the required dependencies by running the following command:
```
pip install -r requirements.txt
```

Usage:

1. Connect the ESP32 microcontroller to the Algae Tree bioreactor device and connect it to your local WiFi network.

2. Configure the config.py file with your WiFi credentials and webserver URL.

3. Upload the main.ino file to the ESP32 microcontroller using the Arduino IDE.

4. Run the following command to start the data collection and sending process:
```
flask --app main run --debug
```
5. Visit the webserver URL to view the data in real-time and graphs.
