# PYTHON CODE: that reads a csv and fills a mongo database with the data
# Collection structure:
# - fecha.
# - nombre de ciudad.
# - latitud.
# - longitud.
# - temperatura máxima.
# - temperatura mínima.

import csv
import pymongo
from pymongo import MongoClient
from datetime import datetime

# Connect to mongo
client = MongoClient('localhost', 27017)

# Create database and collection
db = client['weather']
collection = db['cities']

# Read csv
with open('worldcities.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Convert date to datetime
        date = datetime.strptime(row['fecha'], '%Y-%m-%d')
        # Convert temperature to float
        max_temp = float(row['temperatura_maxima'])
        min_temp = float(row['temperatura_minima'])
        # Insert data
        collection.insert_one({
            'fecha': date,
            'nombre_ciudad': row['nombre_ciudad'],
            'latitud': row['latitud'],
            'longitud': row['longitud'],
            'temperatura_maxima': max_temp,
            'temperatura_minima': min_temp
        })

# Close connection
client.close()

