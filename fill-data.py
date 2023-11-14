import csv
from datetime import datetime
import requests
from app.config.mongo import weather

URL = "https://api.open-meteo.com/v1/forecast?latitude={}&longitude={}&forecast_days=7&daily=temperature_2m_max,temperature_2m_min&timezone=PST"

# Read csv
with open('worldcities.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    cities = []

    for row in reader:
        # request an endpoint with lat and lon
        lat = row['lat']
        lon = row['lng']
        url = URL.format(lat, lon)
        response = requests.get(url)

        # response structure
        range_size = len(response.json()['daily']['time'])
        for i in range(0, range_size):
            # Collect data for batch insert
            obj = {
                'fecha': response.json()['daily']['time'][i],
                'nombre de ciudad': row['city'],
                'latitud': row['lat'],
                'longitud': row['lng'],
                'temperatura máxima': response.json()['daily']['temperature_2m_max'][i],
                'temperatura mínima': response.json()['daily']['temperature_2m_min'][i]
            }
            cities.append(obj)

            # Batch insert every 1000 records (adjust as needed)
            if len(cities) >= 1000:
                print("Inserting 1000 records...")
                weather.insert_many(cities)
                cities = []

    # Insert any remaining records
    if cities:
        weather.insert_many(cities)
