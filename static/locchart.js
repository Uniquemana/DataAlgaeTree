// Function to create the chart using Chart.js
function createChart(ctx, chartData) {
  // Extract data from the chartData object
  var labels = chartData.labels;
  var co2Values = chartData.datasets[0].data;

  // Create the chart
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'CO2 Data',
        data: co2Values,
        backgroundColor: 'rgba(175, 248, 78, 0.5)',
        borderColor: 'rgba(175, 248, 78, 1)',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
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
