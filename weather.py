import requests
from openmeteopy import OpenMeteo
from openmeteopy.hourly import HourlyForecast
from openmeteopy.daily import DailyForecast
from openmeteopy.options import ForecastOptions

def getCoordinates(name):
    """
    Fetches coordinates (latitude and longitude) for a given location name using OpenStreetMap Nominatim API.
    """
    # Construct the API URL with the location name
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={name}"
    headers = {
        'User-Agent': 'WeatherAppProject'
    }
    response = requests.get(url, headers=headers)

    # Check if the response is successful
    if response.status_code == 200:
        data = response.json()
        if data and len(data) > 0:
            # Extract latitude and longitude from the response
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon
        else:
            return None
    else:
        print(f"Error: {response.status_code}")
        return None

def getResults(coords):
    """
    Fetches weather data (both hourly and daily forecasts) for given coordinates using OpenMeteo.
    """
    lat, lon = coords

    # Initialize hourly and daily forecast objects
    hourly = HourlyForecast()
    daily = DailyForecast()

    # Create forecast options with given coordinates
    options = ForecastOptions(lat, lon)

    # Create OpenMeteo objects for temperature and weather code
    temperature = OpenMeteo(options, hourly.temperature_2m(), daily.temperature_2m_max())
    weather_code = OpenMeteo(options, hourly.weathercode(), daily.weathercode())
    
    # Fetch data in pandas DataFrame format
    return temperature.get_pandas() and weather_code.get_pandas()