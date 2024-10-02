import requests
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

def get_coordinates(name):
    """
    Fetches coordinates (latitude and longitude) for a given location name using OpenStreetMap Nominatim API.

    Args:
        name (str): The name of the location.

    Returns:
        tuple: Latitude and longitude of the location or None if not found.
    """
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={name}"
    headers = {'User-Agent': 'WeatherAppProject'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon
        else:
            print("Location not found.")
            return None

    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None

def get_results(coords):
    """
    Fetches weather data (both hourly and daily forecasts) for given coordinates using OpenMeteo.

    Args:
        coords (tuple): Latitude and longitude.

    Returns:
        tuple: DataFrames containing hourly and daily weather data.
    """
    # Setup request caching and retry
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    
    lat, lon = coords
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "precipitation_probability", "weather_code"],
        "daily": ["weather_code", "temperature_2m_max", "sunrise", "sunset", "precipitation_probability_max"]
    }
    
    try:
        response = openmeteo.weather_api(url, params=params)[0]

        # Process hourly data
        hourly = response.Hourly()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
            "precipitation_probability": hourly.Variables(1).ValuesAsNumpy(),
            "weather_code": hourly.Variables(2).ValuesAsNumpy()
        }
        hourly_dataframe = pd.DataFrame(hourly_data)
        
        # Process daily data
        daily = response.Daily()
        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            ),
            "weather_code": daily.Variables(0).ValuesAsNumpy(),
            "temperature_2m_max": daily.Variables(1).ValuesAsNumpy(),
            "precipitation_probability_max": daily.Variables(4).ValuesAsNumpy()
        }
        daily_dataframe = pd.DataFrame(daily_data)
        
        return hourly_dataframe, daily_dataframe

    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return pd.DataFrame(), pd.DataFrame()