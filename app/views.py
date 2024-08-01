from flask import Flask, render_template, request
from app import app
from weather import getCoordinates, getResults
import pandas as pd
from datetime import datetime, timedelta

# Maps for weather images based on weather codes
weather_image_map = {
    0: "images/sunny.png",
    1: "images/clouds_sun.png",
    2: "images/clouds_sun.png",
    3: "images/cloudy.png",
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
    1: "images/ncloudy.png",
    2: "images/ncloudy.png",
    3: "images/cloudy.png",
    51: "images/drizzle.png",
    53: "images/drizzle.png",
    55: "images/drizzle.png",
    56: "images/drizzle.png",
    57: "images/drizzle.png",
    61: "images/nrainy.png",
    63: "images/nrainy.png",
    65: "images/nrainy.png",
    66: "images/nrainy.png",
    67: "images/nrainy.png",
    71: "images/snow.png", 
    73: "images/snow.png",
    75: "images/snow.png",
    80: "images/shower.png",
    81: "images/shower.png",
    82: "images/shower.png",
    95: "images/storm.png",
}

# Route to handle weather requests
@app.route("/weather", methods=["GET", "POST"])
def home():
    coordinates = None
    place = None
    daily_data = []
    hourly_data = []

    # Handle form submission
    if request.method == "POST":
        place = request.form.get('inputText')
        if place:
            coordinates = getCoordinates(place)
            if coordinates is None:
                place = "Location not found for the given place."
            else:
                data = getResults(coordinates)
                hourly_data_df, daily_data_df = data

                # Process daily data
                if isinstance(daily_data_df, pd.DataFrame):
                    daily_data = daily_data_df.reset_index().to_dict(orient='records')
                    for day in daily_data:
                        weather_code = day['weathercode']
                        day['image'] = weather_image_map.get(weather_code, "default.png")

                # Process hourly data
                if isinstance(hourly_data_df, pd.DataFrame):
                    hourly_data = hourly_data_df.reset_index().to_dict(orient='records')
                    current_datetime = datetime.now()
                    next_24_hours = current_datetime + timedelta(hours=24)

                    # Filter hourly data for the next 24 hours
                    hourly_data = [
                        hour for hour in hourly_data
                        if current_datetime <= datetime.strptime(hour['time'], '%Y-%m-%dT%H:%M') < next_24_hours
                    ]

                    # Add appropriate image based on time of day
                    for hour in hourly_data:
                        weather_code = hour['weathercode']
                        hour_datetime = datetime.strptime(hour['time'], '%Y-%m-%dT%H:%M')
                        hour_of_day = hour_datetime.hour

                        if 22 <= hour_of_day or hour_of_day <= 6:
                            hour['image'] = weather_image_map_night.get(weather_code, "default.png")
                        else:
                            hour['image'] = weather_image_map.get(weather_code, "default.png")

    # Render the template with the processed data
    return render_template("home.html", title="Home", place=place, daily_data=daily_data, hourly_data=hourly_data, date=datetime.now().date())