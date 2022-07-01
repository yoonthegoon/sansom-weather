import json
import requests
from datetime import datetime, timedelta, timezone


OWM_KEY = json.load(open('config.json'))['WEATHER_OWM_KEY']


def geocoding(q):
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={q}&limit=1&appid={OWM_KEY}'
    j = requests.get(url).json()[0]

    lat = j['lat']
    lon = j['lon']

    return lat, lon


def rev_geocoding(lat, lon):
    url = f'http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={OWM_KEY}'
    j = requests.get(url).json()[0]

    q = f'{j["name"]}, {j["country"]}'

    return q


def degrees_to_cardinal(d):
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    ix = round(d / (360. / len(dirs)))
    return dirs[ix % len(dirs)]


def one_call(lat, lon):
    url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely&units=imperial&appid={OWM_KEY}'
    j = requests.get(url).json()

    location = rev_geocoding(lat, lon)

    timezone_offset = j['timezone_offset']

    tz = timezone(timedelta(seconds=timezone_offset), name=j['timezone'])

    current_j = j['current']
    current = {
        'dt': datetime.fromtimestamp(current_j['dt'] + timezone_offset, tz=tz),
        'sunrise': datetime.fromtimestamp(current_j['sunrise'] + timezone_offset, tz=tz),
        'sunset': datetime.fromtimestamp(current_j['sunset'] + timezone_offset, tz=tz),
        'temp': current_j['temp'],
        'feels_like': current_j['feels_like'],
        'pressure': 0.02953 * current_j['pressure'],
        'humidity': current_j['humidity'],
        'dew_point': current_j['dew_point'],
        'uvi': current_j['uvi'],
        'clouds': current_j['clouds'],
        'visibility': 0.6213712 * current_j['visibility'],
        'wind_speed': current_j['wind_speed'],
        'wind_dir': degrees_to_cardinal(current_j['wind_deg']),
        'weather': {
            'main': current_j['weather'][0]['main'],
            'description': current_j['weather'][0]['description'],
            'icon': current_j['weather'][0]['icon']
        },
        'pop': current_j.get('pop'),
        'rain': current_j.get('rain')['1h'] / 25.4 if current_j.get('rain') else 0,
        'snow': current_j.get('snow')['1h'] / 25.4 if current_j.get('snow') else 0
    }

    hourly_j = j['hourly']
    hourly = [
        {
            'dt': datetime.fromtimestamp(hour['dt'] + timezone_offset, tz=tz),
            'temp': hour['temp'],
            'feels_like': hour['feels_like'],
            'pressure': 0.02953 * hour['pressure'],
            'humidity': hour['humidity'],
            'dew_point': hour['dew_point'],
            'uvi': hour['uvi'],
            'clouds': hour['clouds'],
            'visibility': 0.6213712 * hour['visibility'],
            'wind_speed': hour['wind_speed'],
            'wind_dir': degrees_to_cardinal(hour['wind_deg']),
            'weather': {
                'main': hour['weather'][0]['main'],
                'description': hour['weather'][0]['description'],
                'icon': hour['weather'][0]['icon']
            },
            'pop': hour['pop'],
            'rain': hour.get('rain')['1h'] / 25.4 if hour.get('rain') else 0,
            'snow': hour.get('snow')['1h'] / 25.4 if hour.get('snow') else 0
        }
        for hour in hourly_j
    ]

    daily_j = j['daily']
    daily = [
        {
            'dt': datetime.fromtimestamp(day['dt'] + timezone_offset, tz=tz),
            'sunrise': datetime.fromtimestamp(day['sunrise'] + timezone_offset, tz=tz),
            'sunset': datetime.fromtimestamp(day['sunset'] + timezone_offset, tz=tz),
            'moonrise': datetime.fromtimestamp(day['moonrise'] + timezone_offset, tz=tz),
            'moonset': datetime.fromtimestamp(day['moonset'] + timezone_offset, tz=tz),
            'moon_phase': day['moon_phase'],
            'temp': day['temp'],
            'feels_like': day['feels_like'],
            'pressure': 0.02953 * day['pressure'],
            'humidity': day['humidity'],
            'dew_point': day['dew_point'],
            'uvi': day['uvi'],
            'clouds': day['clouds'],
            'wind_speed': day['wind_speed'],
            'wind_dir': degrees_to_cardinal(day['wind_deg']),
            'weather': {
                'main': day['weather'][0]['main'],
                'description': day['weather'][0]['description'],
                'icon': day['weather'][0]['icon']
            },
            'pop': day['pop'],
            'rain': day.get('rain') / 25.4 if day.get('rain') else 0,
            'snow': day.get('snow') / 25.4 if day.get('snow') else 0
        }
        for day in daily_j
    ]

    alerts_j = j.get('alerts')
    alerts = [
        {
            'sender_name': alert['sender_name'],
            'event': alert['event'],
            'start': None,
            'end': None,
            'description': alert['description'],
            'tags': alert['tags']
        }
        for alert in alerts_j
    ] if alerts_j else None

    response = {
        'location': location,
        'current': current,
        'hourly': hourly,
        'daily': daily,
        'alerts': alerts
    }

    return response
