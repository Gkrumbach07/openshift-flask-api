import os
from flask import Flask, request
import json
import pandas as pd
from flask_cors import CORS
from urllib.parse import urlencode


app = Flask(__name__)
CORS(app)

DEFAULT_BASE_URL = "http://solarforecaster:8080/%s"


@app.route("/")
def main():
    return "API Root"


def f_to_c(t):
    return (t - 32) * (5/9)


def c_to_f(t):
    return (t * (9/5)) + 32


# uses C degrees and percent
def temp_hum_to_dew(temp, humidity):
    return (Math.pow((humidity/100), 0.125) * (112 + (0.9 * temp))) + (0.1 * temp) - 112


def code_to_value(code, to_compare):
    if(code == to_compare):
        return 6
    else:
        return 0


def getAvg(key, obj):
    return ((obj[key][0]['min'].value + obj[key][1]['max'].value) / 2)


def make_params(temperature, dew_point, relative_humidity, daily_precipitation,
        station_pressure, wind_speed, hourly_visibility=10, weather_code=0):
        return {
            'temperature': temperature,
            'dew_point': dew_point,
            'relative_humidity': relative_humidity,
            'daily_precipitation': daily_precipitation,
            'station_pressure': station_pressure,
            'wind_speed': wind_speed,
            'hourly_visibility': hourly_visibility,
            'cloud_cover': 0,
            'mostly_cloudy': code_to_value(weather_code, 'mostly_cloudy'),
            'mostly_clear': code_to_value(weather_code, 'mostly_clear'),
            'clear': code_to_value(weather_code, 'clear'),
            'cloudy': code_to_value(weather_code, 'cloudy'),
            'partly_cloudy': code_to_value(weather_code, 'partly_cloudy'),
            'overcast': code_to_value(weather_code, 'overcast'),
            'rain_light': code_to_value(weather_code, 'rain_light'),
            'tstorm': code_to_value(weather_code, 'tstorm'),
            'drizzle': code_to_value(weather_code, 'drizzle'),
            'rain_heavy': code_to_value(weather_code, 'rain_heavy'),
            'rain': code_to_value(weather_code, 'rain'),
            'fog': code_to_value(weather_code, 'fog'),
            'snow_light': code_to_value(weather_code, 'snow_light'),
            'snow': code_to_value(weather_code, 'snow'),
            'snow_heavy': code_to_value(weather_code, 'snow_heavy'),
            'freezing_rain': code_to_value(weather_code, 'freezing_rain'),
            'freezing_drizzle': code_to_value(weather_code, 'freezing_drizzle'),
            'ice_pellets': code_to_value(weather_code, 'ice_pellets'),
            'ice_pellets_light': code_to_value(weather_code, 'ice_pellets_light'),
            'ice_pellets_heavy': code_to_value(weather_code, 'ice_pellets_heavy'),
            'flurries': code_to_value(weather_code, 'flurries'),
            'freezing_rain_heavy': code_to_value(weather_code, 'freezing_rain_heavy'),
            'freezing_rain_light': code_to_value(weather_code, 'freezing_rain_light'),
            'fog_light': code_to_value(weather_code, 'fog_light')
        }


def score_text(text, url = None):
    url = (url or (DEFAULT_BASE_URL % "predict"))
    if type(text) == str:
        text = [text]
    payload = urlencode({"json_args" : json.dumps(text)})
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.request("POST", url, data=payload, headers=headers)
    return json.loads(response.text)


def make_prediction(lat, long):
    url = "https://api.climacell.co/v3/weather/forecast/daily"

    querystring = {
    "lat":lat,
    "lon":long,
    "unit_system":"us",
    "start_time":"now",
    "fields":"precipitation,precipitation_accumulation,temp,\
     wind_speed,baro_pressure,visibility,humidity,weather_code"
    "apikey":"9HaH9EKcMl4ANqi3eBna6kH58fybWmTu"}

    response = requests.request("GET", url, params=querystring)

    weather_data = json.loads(response.text)

    # grab solar predictions based on forecast
    params = []
    for day in weather_data:
        params.append(make_params(
          this.getAvg("temp", day),
          temp_hum_to_dew(f_to_c(this.getAvg("temp", day)), this.getAvg("humidity", day)),
          this.getAvg("humidity", day),
          day['precipitation_accumulation'].value,
          this.getAvg("baro_pressure", day),
          this.getAvg("wind_speed", day),
          this.getAvg("visibility", day),
          day['weather_code'].value))

    # make predict call
    return {
    "weather": weather_data,
    "solar": score_text(params)
    }


@app.route("/predict", methods=['POST'])
def predict():
    if 'json_args' in request.form:
        args = pd.read_json(request.form['json_args'])
        return make_prediction(args['lat'], args['long'])


@qpp.route("/addlocation", methods=['POST'])
def add_location():
    if 'json_args' in request.form:
        args = pd.read_json(request.form['json_args'])
        with open('database.json', "r+") as json_file:
            data = json.load(json_file)
            data['locations'].append({
                "id": len(data['locations']) + 1,
                "lat": args["lat"],
                "long": args["long"]
            })
            json_file.seek(0)
            json.dump(data, json_file)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)