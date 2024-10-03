from flask import render_template, request
from app import app
from weather import get_coordinates, get_results
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Maps for weather images based on weather codes
weather_image_map = {
    0: "images/sunny.png",
    1: "images/clouds_sun.png",
    2: "images/clouds_sun.png",
    3: "images/cloudy.png",
    45: "images/foggy.png",
    48: "images/foggy.png",
    51: "images/drizzle.png",
    53: "images/drizzle.png",
    55: "images/drizzle.png",
    56: "images/drizzle.png",
    57: "images/drizzle.png",
    61: "images/rain.png",
    63: "images/rain.png",
    65: "images/rain.png",
    66: "images/rain.png",
    67: "images/rain.png",
    71: "images/snow.png",
    73: "images/snow.png",
    75: "images/snow.png",
    80: "images/shower.png",
    81: "images/shower.png",
    82: "images/shower.png",
    95: "images/storm.png",
}

weather_image_map_night = {
    0: "images/night.png",
    1: "images/cloudy_night.png",
    2: "images/cloudy_night.png",
    3: "images/cloudy.png",
    45: "images/foggy.png",
    48: "images/foggy.png",
    51: "images/drizzle.png",
    53: "images/drizzle.png",
    55: "images/drizzle.png",
    56: "images/drizzle.png",
    57: "images/drizzle.png",
    61: "images/rain_night.png",
    63: "images/rain_night.png",
    65: "images/rain_night.png",
    66: "images/rain_night.png",
    67: "images/rain_night.png",
    71: "images/snow.png",
    73: "images/snow.png",
    75: "images/snow.png",
    80: "images/shower.png",
    81: "images/shower.png",
    82: "images/shower.png",
    95: "images/storm.png",
}

# Route to handle weather requests
@app.route("/", methods=["GET", "POST"])
def home():
    coordinates = None
    place = None
    daily_data = []
    hourly_data = []

    if request.method == "POST":
        place = request.form.get('inputText')
        if place:
            coordinates = get_coordinates(place)
            if coordinates:
                hourly_data_df, daily_data_df = get_results(coordinates)

                if isinstance(daily_data_df, pd.DataFrame):
                    daily_data = daily_data_df.reset_index().to_dict(orient='records')
                    for day in daily_data:
                        weather_code = day.get('weather_code')
                        day['image'] = weather_image_map.get(weather_code, "default.png")

                if isinstance(hourly_data_df, pd.DataFrame):
                    hourly_data = hourly_data_df.reset_index().to_dict(orient='records')
                    current_datetime = datetime.now(pytz.UTC)
                    next_7_days = current_datetime + timedelta(days=7)

                    hourly_data = [
                        hour for hour in hourly_data
                        if current_datetime <= hour['date'] < next_7_days
                    ]

                    for hour in hourly_data:
                        weather_code = hour.get('weather_code')
                        hour_datetime = hour['date']
                        hour_of_day = hour_datetime.hour

                        image_map = weather_image_map if 6 <= hour_of_day and hour_of_day <= 21 else weather_image_map_night
                        hour['image'] = image_map.get(weather_code, "default.png")

    return render_template("home.html", title="Home", place=place, daily_data=daily_data, hourly_data=hourly_data, date=datetime.now(pytz.UTC).date())
