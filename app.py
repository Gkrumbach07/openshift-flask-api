import os
from flask import Flask, request
import json
from flask_cors import CORS
from urllib.parse import urlencode
import requests
from datetime import datetime
import argparse


app = Flask(__name__)
CORS(app)


@app.route("/")
def main():
    return "API Root"


@app.route("/predict", methods=['POST'])
def predict():
    if 'json_args' in request.form:
        args = json.loads(request.form['json_args'][0])
        return make_prediction(args['lat'], args['long'])


@app.route("/addlocation", methods=['POST'])
def add_location():
    if 'json_args' in request.form:
        args = json.loads(request.form['json_args'])
        with open('database.json', "r+") as json_file:
            data = json.load(json_file)
            data['locations'].append({
                "id": len(data['locations']) + 1,
                "lat": args["lat"],
                "long": args["long"]
            })
            json_file.seek(0)
            json.dump(data, json_file)

            return data



@app.route("/tracked")
def getTracked():
    with open('database.json') as json_file:
        data = json.load(json_file)
        out = {"locations": []}
        for loc in data['locations']:
             out['locations'].append({
                "id": loc['id'],
                "lat": loc["lat"],
                "long": loc["long"],
                "start_day": datetime.today().strftime('%Y-%m-%d'),
                "solar": make_prediction(loc['lat'], loc['long'])["solar"]
             })
        return out


def get_arg(env, default):
    return os.getenv(env) if os.getenv(env, '') is not '' else default


def parse_args(parser):
    args = parser.parse_args()
    args.apikey = get_arg('API_KEY', args.apikey)
    args.url = get_arg('REACT_APP_MODEL_URL', args.url)
    return args


def f_to_c(t):
    return (t - 32) * (5/9)


def c_to_f(t):
    return (t * (9/5)) + 32


# uses C degrees and percent
def temp_hum_to_dew(temp, humidity):
    return (pow((humidity/100), 0.125) * (112 + (0.9 * temp))) + (0.1 * temp) - 112


def code_to_value(code, to_compare):
    if(code == to_compare):
        return 6
    else:
        return 0


def getAvg(key, obj):
    return ((obj[key][0]['min']['value'] + obj[key][1]['max']['value']) / 2)


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
    url = args.url + "/predict"
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
    "fields":"precipitation,precipitation_accumulation,temp,wind_speed,baro_pressure,visibility,humidity,weather_code",
    "apikey": args.apikey
    }

    response = requests.request("GET", url, params=querystring)

    weather_data = json.loads(response.text)

    # grab solar predictions based on forecast
    params = []
    for day in weather_data:
        params.append(make_params(
          getAvg("temp", day),
          temp_hum_to_dew(f_to_c(getAvg("temp", day)), getAvg("humidity", day)),
          getAvg("humidity", day),
          day['precipitation_accumulation']['value'],
          getAvg("baro_pressure", day),
          getAvg("wind_speed", day),
          getAvg("visibility", day),
          day['weather_code']['value']))

    # make predict call
    return {
    "weather": weather_data,
    "solar": score_text(params)
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='backend service')
    parser.add_argument(
            '--apikey',
            help='ClimaCell api key, env variable API_KEY',
            default='0000')
    parser.add_argument(
            '--url',
            help='model base url, env variable REACT_APP_MODEL_URL',
            default='http://solarforecaster:8080')
    args = parse_args(parser)
    app.run(host="0.0.0.0", port=8080)