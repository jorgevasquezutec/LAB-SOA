
import requests
import xml.etree.ElementTree as ET
from fastapi.exceptions import HTTPException
from app.config.unleash import unleash_client
apis = {
    "geo": "https://geocoding-api.open-meteo.com/v1/search?name={}",
    "nomi": "https://nominatim.openstreetmap.org/search?q={}&format=json",
}

app_context = {"user_id": "prueba@email.com"}

DELTA = 0.01

def fetch_data(api_url):
    response = requests.get(api_url)
    return response.json()

def fetch_data_xml(api_url):
    response = requests.get(api_url)
    root = ET.fromstring(response.content)
    return root

def create_bounding_box(latitude, longitude, delta):
      # Calculate the latitude and longitude for the upper-left corner of the bounding box
    upper_left_lat = round(latitude - delta, 7)
    upper_left_lon = round(longitude - delta, 7)

    # Calculate the latitude and longitude for the lower-right corner of the bounding box
    lower_right_lat = round(latitude + delta, 7)
    lower_right_lon = round(longitude + delta, 7)
    return (upper_left_lat, upper_left_lon, lower_right_lat, lower_right_lon)



def getLatitudLongitud(ciudad):
    ciudad = ciudad.lower()
    geocoding = unleash_client.is_enabled("geocoding", context=app_context)
    currentApi = apis["geo"] if geocoding else apis["nomi"]
    URL = currentApi.format(ciudad)
    print(URL)
    data = fetch_data(URL)
    # print(len(data))
    if(len(data) == 0):
        print("no se encontro")
        raise HTTPException(status_code=404,detail="No se encontro la ciudad")
    if(geocoding):
        lat = data['results'][0]['latitude']
        lat = float(lat)
        lon = data['results'][0]['longitude']
        lon = float(lon)
        return lat, lon
    lat = data[0]['lat']
    lat = float(lat)
    lon = data[0]['lon']
    lon = float(lon)
    return lat, lon


def getResutaranteBYBox(box):
    URL = 'https://api.openstreetmap.org/api/0.6/map?bbox='+str(box[1])+','+str(box[0])+','+str(box[3])+','+str(box[2])
    data = fetch_data_xml(URL)
    return data

def getXMLRestaurantes(res):
    rdata = []
    for element in res:
        # print(element)
        restaurant_info = {}
        # Iterar a través de los tags del elemento
        for tag in element:
            if 'k' in tag.attrib and 'v' in tag.attrib:
                k = tag.attrib['k']
                v = tag.attrib['v']
                restaurant_info[k] = v
        
        # Verificar si el elemento representa un restaurante
        if 'amenity' in restaurant_info and restaurant_info['amenity'] == 'restaurant':
            rdata.append(restaurant_info)
    # print(rdata)
    return rdata


def get_restaurants(ciudad: str):
    lat,long = getLatitudLongitud(ciudad)
    # print(lat,long)
    box = create_bounding_box(lat,long,DELTA)
    # print(box)
    data = getResutaranteBYBox(box)
    # print(data)
    restaurants = getXMLRestaurantes(data)
    return restaurants


def getDailyWeatherByDate(ciudad: str, date: str):
    lat,long = getLatitudLongitud(ciudad)
    #https://api.open-meteo.com/v1/forecast?latitude=-12.0432&longitude=-77.0282&daily=temperature_2m_max,temperature_2m_min&timezone=PST&start_date=2023-10-05&end_date=2023-10-05
    URL = 'https://api.open-meteo.com/v1/forecast?latitude='+str(lat)+'&longitude='+str(long)+'&daily=temperature_2m_max,temperature_2m_min&timezone=PST&start_date='+date+'&end_date='+date
    data = fetch_data(URL) #temperature_2m_max
    temperature_max = data['daily']['temperature_2m_max'][0]
    temperature_min = data['daily']['temperature_2m_min'][0]
    return lat, long , temperature_max, temperature_min
    

def getDailyWeather(ciudad: str):
    lat,long = getLatitudLongitud(ciudad)
    #https://api.open-meteo.com/v1/forecast?latitude=-12.04&longitude=-77.03&forecast_days=2&daily=temperature_2m_max&timezone=PST
    URL = 'https://api.open-meteo.com/v1/forecast?latitude='+str(lat)+'&longitude='+str(long)+'&forecast_days=7&daily=temperature_2m_max&timezone=PST'
    data = fetch_data(URL) #temperature_2m_max
    # pair up (time,temperature_2m_max)
    result = []
    for i in range(len(data['daily']['temperature_2m_max'])):
        obj = {}
        key = data['daily']['time'][i]
        obj[key] = data['daily']['temperature_2m_max'][i]
        result.append(obj)
        
    return result

def getHourlyWeather(ciudad: str):
    lat,long = getLatitudLongitud(ciudad)
    # print(lat,long)
    #https://api.open-meteo.com/v1/forecast?latitude=-12.04&longitude=-77.03&forecast_days=2&hourly=temperature_2m&timezone=PST
    URL = 'https://api.open-meteo.com/v1/forecast?latitude='+str(lat)+'&longitude='+str(long)+'&forecast_days=2&hourly=temperature_2m&timezone=PST'
    # print(URL)
    data = fetch_data(URL)#temperature_2m
    # print(data)
    # pair up (time,temperature_2m)
    result = []
    for i in range(len(data['hourly']['temperature_2m'])):
        obj = {}
        key = data['hourly']['time'][i]
        obj[key] = data['hourly']['temperature_2m'][i]
        result.append(obj)
    return result