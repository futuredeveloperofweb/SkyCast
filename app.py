import logging
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Weather API URL and API key
WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/forecast'
API_KEY = '19bbceda689962e4fcce5f69e5bbf611'

# Sample data for supported locations
SUPPORTED_LOCATIONS = ['New York', 'Los Angeles', 'London', 'Tokyo']

# Sample user preferences
USER_PREFERENCES = {
    'userId1': {
        'notifications': True,
        'units': 'metric'
    },
    'userId2': {
        'notifications': False,
        'units': 'imperial'
    }
}

@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

@app.route('/api/weather')
def get_weather():
    """
    Returns weather forecast data for a specified location.

    Parameters:
    - location: Latitude and longitude OR city name

    Returns:
    - Weather forecast data for the specified location.
    """
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'Location parameter is required'}), 400

    # Fetch weather data from API
    params = {
        'q': location,
        'appid': API_KEY
    }
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        weather_data = response.json()
        return jsonify(weather_data)
    except requests.RequestException as e:
        logger.error(f'Error fetching weather data: {e}')
        return jsonify({'error': 'Error fetching weather data'}), 500

@app.route('/api/locations')
def get_locations():
    """
    Returns a list of supported locations for weather forecasts.

    Returns:
    - List of supported locations.
    """
    return jsonify(SUPPORTED_LOCATIONS)

@app.route('/api/user/preferences', methods=['GET', 'POST'])
def user_preferences():
    """
    Returns or updates user preferences for weather notifications and units.

    GET Parameters:
    - userId: User ID

    Returns:
    - User preferences for weather notifications and units.

    POST Parameters:
    - userId: User ID
    - notifications: Boolean value indicating whether to receive notifications
    - units: Preferred units for weather data (metric or imperial)

    Returns:
    - Updated user preferences.
    """
    if request.method == 'GET':
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({'error': 'userId parameter is required'}), 400
        if user_id not in USER_PREFERENCES:
            return jsonify({'error': 'User preferences not found'}), 404
        return jsonify(USER_PREFERENCES[user_id])
    elif request.method == 'POST':
        data = request.json
        user_id = data.get('userId')
        notifications = data.get('notifications')
        units = data.get('units')

        if not all([user_id, notifications, units]):
            return jsonify({'error': 'userId, notifications, and units are required'}), 400

        USER_PREFERENCES[user_id] = {
            'notifications': notifications,
            'units': units
        }
        return jsonify(USER_PREFERENCES[user_id])

@app.errorhandler(404)
def page_not_found(e):
    """Custom error handler for 404 Not Found."""
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(Exception)
def handle_error(e):
    """Global error handler."""
    logger.error(f'Unhandled Exception: {e}')
    return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
