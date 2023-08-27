// Function to create the chart using Chart.js
function createChart(ctx, chartData) {
  // Extract data from the chartData object
  var labels = chartData.labels;
  var co2Values = chartData.datasets[0].data;
  var air_temp_values = chartData.datasets[1].data;
  var air_humid_values = chartData.datasets[2].data;
  var left_water_temp_valaues = chartData.datasets[3].data;
  var right_water_temp_valaues = chartData.datasets[4].data;
  var tower_led_pwm = chartData.datasets[5].data;

  // const currentTime = new Date();
  // const minDate = new Date(currentTime - 500 * 60 * 60 * 1000); // 48 hours in milliseconds

  // Create the chart
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
      {
        pointRadius: 0, // disable for a single dataset
        spanGaps: true, // enable for a single dataset
        label: 'CO2 Data',
        data: co2Values,
        backgroundColor: 'rgba(175, 248, 78, 0.5)',
        borderColor: 'rgba(175, 248, 78, 1)',
        borderWidth: 2
      },
      {
        label: 'Air Temperature',
        data: air_temp_values,
        backgroundColor:'rgba(239, 98, 98, 0.5)',
        borderColor: 'rgba(239, 98, 98, 1)',
        borderWidth: 2,
        hidden: true
      },
      {
        label: 'Air Humidity',
        data: air_humid_values,
        backgroundColor:'rgba(79, 192, 208, 0.5)',
        borderColor: 'rgba(79, 192, 208, 1)',
        borderWidth: 2,
        hidden: true
      },
      {
        label: 'Left Water Temperature',
        data: left_water_temp_valaues,
        backgroundColor:'rgba(20, 195, 142, 0.5)',
        borderColor: 'rgba(20, 195, 142, 1)',
        borderWidth: 2,
        hidden: true
        
      },
      {
        label: 'Right Water Temperature',
        data: right_water_temp_valaues,
        backgroundColor:'rgba(79, 192, 208, 0.5)',
        borderColor: 'rgba(79, 192, 208, 1)',
        borderWidth: 2,
        hidden: true
      },
      {
        label: 'Tower LED PWM',
        data: tower_led_pwm,
        backgroundColor:'rgba(79, 192, 208, 0.5)',
        borderColor: 'rgba(79, 192, 208, 1)',
        borderWidth: 2,
        hidden: true
      }
    ]
    },
    options: {
      responsive: true,
      // maintainAspectRatio: false,
      // animation: false,
      // spanGaps: true, // enable for all datasets
      // scales: {
      //   x: {
      //     type: 'time',
      //     time: {
      //         parser: function(value) {
      //             return moment(value, 'MM-DD HH:mm'); // Adjust the format as needed
      //         },
      //         min: minDate,
      //         unit: 'hour'
      //     }
      //   }
      // }
    }
  });
}

// Function to update the chart data
function updateChart(range) {
  // Perform an AJAX request to get the updated chart data
  // You can modify this part to fetch data from the server if needed
  // For simplicity, let's assume the data is already available in the variable 'chartData'

  // Update the chart with the new data
  var ctx = document.getElementById('co2Chart').getContext('2d');
  createChart(ctx, chartData);
}

// Function to handle the DOMContentLoaded event
document.addEventListener('DOMContentLoaded', function () {
  // Parse the JSON data passed from the Flask app
  var chartData = JSON.parse('{{ chart_json|safe }}');

  // Get the chart canvas element
  var canvas = document.getElementById('co2Chart');

  // Create the chart using Chart.js
  createChart(canvas.getContext('2d'), chartData);
});
