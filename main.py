from flask import Flask, render_template, request

app = Flask(__name__)

# Dictionary to store the data for each device
device_data = {}

@app.route('/<device_id>')
def show_data(device_id):
    if device_id not in device_data:
        return 'No data available for device ' + device_id
    else:
        data = device_data[device_id]
        return render_template('data.html', data=data, device_id=device_id)

@app.route('/', methods=['POST'])
def receive_data():
    data_str = request.data.decode('utf-8')
    data_list = data_str.strip().split('\n')
    for data in data_list:
        device_id, co2, air_temp, air_humid, leftwatertemp, rightwatertemp,leftheatertemp, rightheatertemp, leftheaterpwm, rightheaterpwm ,led = data.split()
        # Update the data in the dictionary
        device_data[device_id] = [(co2, air_temp, air_humid, leftwatertemp, rightwatertemp,leftheatertemp, rightheatertemp, leftheaterpwm, rightheaterpwm, led)]
    return 'Data received successfully'

if __name__ == '__main__':
    app.run(debug=True)
