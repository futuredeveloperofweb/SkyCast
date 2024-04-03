import logging
from flask import Flask, render_template, request, jsonify
import requests

# Initialize Flask app
app = Flask(__name__)

# Configure logging for debugging and operational insights
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for the OpenWeatherMap API
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/forecast"
API_KEY = "19bbceda689962e4fcce5f69e5bbf611"

# Predefined list of supported locations for weather forecasting
SUPPORTED_LOCATIONS = ["New York", "Los Angeles", "London", "Tokyo"]

# Mock user preferences for demonstration purposes
USER_PREFERENCES = {
    "userId1": {"notifications": True, "units": "metric"},
    "userId2": {"notifications": False, "units": "imperial"},
}


@app.route("/")
def index():
    """
    Route to render the index page with weather data for supported locations.
    Fetches weather data for each location in SUPPORTED_LOCATIONS and passes
    the data to the frontend for rendering.
    """
    weather_data = []
    for location in SUPPORTED_LOCATIONS:
        params = {"q": location, "appid": API_KEY, "units": "metric"}
        response = requests.get(WEATHER_API_URL, params=params)
        if response.ok:
            data = process_forecast_data(response.json())
            weather_data.append(data)
    return render_template("weather.html", weather_data=weather_data)


@app.route("/weather", methods=["GET"])
def get_weather():
    """
    API endpoint to fetch weather data for a given location.
    Returns processed weather data including current conditions and forecast.
    """
    location = request.args.get("location")
    if not location:
        return jsonify({"error": "Location parameter is required"}), 400

    params = {"q": location, "appid": API_KEY, "units": "metric"}
    try:
        forecast_response = requests.get(WEATHER_API_URL, params=params)
        forecast_response.raise_for_status()  # Raises an error for bad responses
        forecast_data = forecast_response.json()
        processed_data = process_forecast_data(forecast_data)
        return jsonify(processed_data)
    except requests.RequestException as e:
        logger.error(f"Error fetching weather data for {location}: {e}")
        return jsonify({"error": "Error fetching weather data"}), 500


def process_forecast_data(forecast_data):
    """
    Simplifies the weather forecast data structure for easier frontend usage.

    Args:
        forecast_data: The complete forecast data returned from the API.

    Returns:
        A simplified dictionary with relevant weather details.
    """
    processed = {
        "city": forecast_data["city"]["name"],
        "today": {
            "temperature": forecast_data["list"][0]["main"]["temp"],
            "description": forecast_data["list"][0]["weather"][0]["description"],
            "icon": f"http://openweathermap.org/img/w/{forecast_data['list'][0]['weather'][0]['icon']}.png",
            "humidity": forecast_data["list"][0]["main"]["humidity"],
            "wind_speed": forecast_data["list"][0]["wind"]["speed"],
        },
        "forecast": [
            {
                "date": entry["dt_txt"],
                "icon": f"http://openweathermap.org/img/w/{entry['weather'][0]['icon']}.png",
                "temp_max": entry["main"]["temp_max"],
                "temp_min": entry["main"]["temp_min"],
            }
            for entry in forecast_data["list"][1:4]
        ],
    }
    return processed


@app.route("/api/locations")
def get_locations():
    """
    Returns a list of supported locations for weather forecasts.
    """
    return jsonify(SUPPORTED_LOCATIONS)


@app.route("/api/user/preferences", methods=["GET", "POST"])
def user_preferences():
    """
    Endpoint to get or update user preferences including notifications and units.

    GET Parameters:
        userId: Identifier for the user whose preferences are being requested.

    POST Parameters:
        userId: Identifier for the user.
        notifications: Boolean indicating whether to receive notifications.
        units: Preferred units for displaying weather data ('metric' or 'imperial').
    """
    if request.method == "GET":
        user_id = request.args.get("userId")
        if not user_id:
            return jsonify({"error": "userId parameter is required"}), 400
        if user_id not in USER_PREFERENCES:
            return jsonify({"error": "User preferences not found"}), 404
        return jsonify(USER_PREFERENCES[user_id])
    elif request.method == "POST":
        data = request.json
        user_id = data.get("userId")
        notifications = data.get("notifications")
        units = data.get("units")
        if not all([user_id, isinstance(notifications, bool), units]):
            return jsonify({"error": "Invalid input for user preferences"}), 400
        USER_PREFERENCES[user_id] = {"notifications": notifications, "units": units}
        return jsonify(USER_PREFERENCES[user_id])


@app.errorhandler(404)
def page_not_found(e):
    """
    Custom error handler for 404 Not Found errors.
    """
    return jsonify({"error": "Page not found"}), 404


@app.errorhandler(Exception)
def handle_error(e):
    """
    Global error handler for catching unhandled exceptions.
    """
    logger.error(f"Unhandled Exception: {e}")
    return jsonify({"error": "Internal Server Error"}), 500


if __name__ == "__main__":
    app.run(debug=True)
