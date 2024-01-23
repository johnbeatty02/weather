import requests
from datetime import datetime, timedelta
import smtplib

# OpenWeatherMap API credentials
OWM_API_KEY = '7ca5472629e39b7d3b13c2fc04d850ca'
latitude = '42.34947'
longitude = '-71.08407'

# AccuWeather API credentials
ACCUWEATHER_API_KEY = '3kYRbNaQuQaxCFHbYJGyJv0ii74tBwnb'
LOCATION_KEY = '2089380'
hourly_forecast_url = f'https://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{LOCATION_KEY}'

# Email credentials
GMAIL_EMAIL = 'johnbeatty02@gmail.com'
GMAIL_PASSWORD = 'enda ktwd qbgx mqxq'  # Application-specific password
TO_EMAIL = '5089544798@vtext.com'  # Verizon phone number email address


def get_openweathermap_forecast(api_key, latitude, longitude):
    try:
        # OpenWeatherMap One Call API for precipitation data
        api_url = 'https://api.openweathermap.org/data/2.5/onecall'
        params = {'lat': latitude, 'lon': longitude, 'appid': api_key, 'exclude': 'current,minutely,daily', 'units': 'metric'}
        response = requests.get(api_url, params=params)
        response.raise_for_status()

        # Extract rain probability forecast for the next 4 hours
        rain_forecast = [hourly['pop'] for hourly in response.json().get('hourly', [])[:4]]

        return rain_forecast

    except requests.exceptions.RequestException as e:
        print(f"Error making OpenWeatherMap API request: {e}")
        return []


def get_accuweather_forecast(api_key, location_key):
    try:
        # AccuWeather API request
        url = f'https://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{location_key}'
        params = {'apikey': api_key, 'details': 'true'}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error making AccuWeather API request: {e}")
        return None


def format_time(timestamp):
    # Format timestamp to readable time
    return datetime.fromtimestamp(timestamp).strftime('%-I %p').lstrip('0').replace(' 0', ' ')


def send_text_message(message, gmail_email, gmail_password, to_email):
    # Send text message using Gmail
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(gmail_email, gmail_password)
        server.sendmail(gmail_email, to_email, message)


# Get current time and forecast times
local_utc_offset = timedelta(hours=-4)  # Adjusts UTC time for New York time
current_time = datetime.utcnow() + local_utc_offset
forecast_times = [current_time + timedelta(hours=i*3) for i in range(4)]
forecast_times_readable = [forecast_time.strftime('%-I %p') for forecast_time in forecast_times]

# Get OpenWeatherMap rain forecast
rain_forecast = get_openweathermap_forecast(OWM_API_KEY, latitude, longitude)

# Print OpenWeatherMap rain forecast
for i, rain_probability in enumerate(rain_forecast):
    time_str = format_time(forecast_times[i].timestamp())
    print(f"Rain Probability at {time_str}: {round(rain_probability * 100)}%")

# Get AccuWeather hourly forecast
data = get_accuweather_forecast(ACCUWEATHER_API_KEY, LOCATION_KEY)

if data:
    # Format AccuWeather data for temperatures
    real_feel_temperatures = [hour['RealFeelTemperature']['Value'] for hour in data]
    times = [hour['DateTime'] for hour in data]
    labeled_temperatures = [(datetime.fromisoformat(time.replace('Z', '')).strftime("%-I %p"), temp)
                            for time, temp in zip(times, real_feel_temperatures)]
    data_at_3_hour_intervals = labeled_temperatures[::3]

    # Create a message with rain probabilities and temperatures
    weather_message = "\n".join([f"{time}: {round(temp)} F, {round(rain_probability * 100)}%"
                                for time, temp, rain_probability in zip(forecast_times_readable, [temp for _, temp in data_at_3_hour_intervals[:4]], rain_forecast)])

    message = f'Good morning! Here is the forecast for {current_time.strftime("%A, %B %d")}:\n{weather_message}'

    # Print the message
    print(message)

    # Send the text message
    send_text_message(message, GMAIL_EMAIL, GMAIL_PASSWORD, TO_EMAIL)
    print("Test message sent successfully!")
