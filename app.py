from flask import Flask, render_template, request, jsonify
from flask_caching import Cache
import requests

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 600})

# Replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key
API_KEY = '60557feec00447a018f4f28974cae610'

#Frontend
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>World Weather Map</title>
    <!-- Include Leaflet CSS and JS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <style>
        body {
            font-family: Georgia, 'Times New Roman', Times, serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #181c29;
        }

        h1 {
            font-family: Georgia, 'Times New Roman', Times, serif;
            text-align: center;
            margin-top: 20px;
            color: #9ca0b9;
        }

        #map {
            height: 500px;
            width: 80%;
            margin: 20px;
        }

        .highlight-circle {
            fill-opacity: 0.5;
            transition: fill-opacity 0.1s ease-in-out;
        }

        .temperature-key {
            background-color: #181c29;
            padding: 10px;
            border: 1px solid #cbcbcb;
            border-radius: 5px;
            margin-top: 20px;
            display: flex;
            justify-content: space-between;
            width: 80%;
        }

        .legend-item {
            flex: 1;
            text-align: center;
            padding: 5px;
            border: 1px solid #6c6b6b;
            border-radius: 5px;
            margin: 5px;
            font-family: Georgia, 'Times New Roman', Times, serif;
            color: #141722;
        }
    </style>
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
</head>
<body>
    <h1>World Weather Map</h1>
    <div id="map"></div>
    <div class="temperature-key">
        <div class="legend-item" style="background-color: blue;">-10°C and below</div>
        <div class="legend-item" style="background-color: lightblue;">-10°C to 0°C</div>
        <div class="legend-item" style="background-color: green;">0°C to 10°C</div>
        <div class="legend-item" style="background-color: #f4c430;">10°C to 20°C</div>
        <div class="legend-item" style="background-color: red;">20°C and above</div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function () {
            var map = L.map('map').setView([0, 0], 2);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);

            map.on('mousemove', function (e) {
                var lat = e.latlng.lat.toFixed(2);
                var lon = e.latlng.lng.toFixed(2);

                // Fetch current weather data
                fetch(`/get_weather?lat=${lat}&lon=${lon}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.main && data.main.temp) {
                            var temperature = data.main.temp;

                            // Define color based on temperature range
                            var color = getColorByTemperature(temperature);

                            // Highlight the country with the calculated color
                            highlightCountry(e.latlng, color);
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching weather data:', error);
                    });
            });

            function getColorByTemperature(temperature) {
                if (temperature < 0) {
                    return 'blue';
                } else if (temperature < 10) {
                    return 'lightblue';
                } else if (temperature < 20) {
                    return 'green';
                } else if (temperature < 30) {
                    return '#f4c430';
                } else {
                    return 'red';
                }
            }

            function highlightCountry(latlng, color) {
                // Remove existing circles
                map.eachLayer(function (layer) {
                    if (layer instanceof L.Circle) {
                        map.removeLayer(layer);
                    }
                });

                // Add a new highlighted circle
                var circle = L.circle(latlng, {
                    radius: 200000, // Adjust the radius based on your preference
                    color: color,
                    fillOpacity: 0.5,
                    className: 'highlight-circle'  // Add a class for styling
                }).addTo(map);
            }
        });
        function debounce(func, wait, immediate) {
    var timeout;

    return function executedFunction() {
        var context = this;
        var args = arguments;

        var later = function () {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
}};
    </script>
</body>
</html>

    '''

#Lati/longi
@cache.cached(timeout=600)
@app.route('/get_weather', methods=['GET'])
def get_weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    # Fetch current weather data
    current_weather_url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
    current_weather_data = requests.get(current_weather_url).json()

    return jsonify(current_weather_data)

if __name__ == '__main__':
    app.run(debug=True)
