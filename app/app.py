from fastapi import FastAPI, Request, Header, Response
from starlette.middleware.cors import CORSMiddleware
from app.config.settings import api_settings
import uvicorn
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from app.constants.values import LOG_API_PATHS
import requests
# import concurrent.futures
import app.services as services
import xml.etree.ElementTree as ET
from strawberry.asgi import GraphQL
import strawberry


@strawberry.type
class Weather:
    city: str
    temperatureMax: float
    temperatureMin: float
    lat: float
    lon: float
    date: str


@strawberry.type
class Restaurant:
    amenity: str = None
    name: str = None
    cuisine: str = None
    source: str = None
    website: str = None
    opening_hours: str = None
    adress_street: str = None
    adress_city: str = None
    adress_housenumber : str = None

# @strawberry.type
# class Restaurant:


@strawberry.type
class Query:
    @strawberry.field
    def weather(self, ciudad: str, date: str) -> Weather:
        lat, lon, tmax, tmin = services.getDailyWeatherByDate(ciudad, date)
        return Weather(city=ciudad, temperatureMax=tmax, temperatureMin=tmin, lat=lat, lon=lon, date=date)

    @strawberry.field
    def restaurants(self, ciudad: str) -> list[Restaurant]:
        restaurants = services.get_restaurants(ciudad)
        parseRestaurants = []
        for restaurant in restaurants:
            amenity = restaurant['amenity'] if 'amenity' in restaurant else 'Sin amenity'
            name = restaurant['name'] if 'name' in restaurant else 'Sin nombre'
            cuisine = restaurant['cuisine'] if 'cuisine' in restaurant else 'Sin cocina'
            source = restaurant['source'] if 'source' in restaurant else 'Sin fuente'
            opening_hours = restaurant['opening_hours'] if 'opening_hours' in restaurant else 'Sin opening_hours'
            website = restaurant['website'] if 'website' in restaurant else 'Sin website'
            adress_city = restaurant['addr:city'] if 'addr:city' in restaurant else 'Sin addres'
            adress_street = restaurant['addr:street'] if 'addr:street' in restaurant else 'Sin addres'
            adress_housenumber = restaurant['addr:housenumber'] if 'addr:housenumber' in restaurant else 'Sin addres'
            
            parseRestaurants.append(
                Restaurant(amenity=amenity,
                           name=name,
                           cuisine=cuisine,
                           source=source,
                           opening_hours=opening_hours,
                           website=website,
                           adress_street=adress_street,
                           adress_city=adress_city,
                           adress_housenumber=adress_housenumber
                           )
            )
        return parseRestaurants


schema = strawberry.Schema(query=Query)


graphql_app = GraphQL(schema)

app = FastAPI(
    title=api_settings.TITLE,
    openapi_url=f'{api_settings.PREFIX}/openapi.json',
    docs_url=f'{api_settings.PREFIX}/docs',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# set prefix  all routes

app.router.prefix = api_settings.PREFIX


app.add_route(f'{api_settings.PREFIX}/graphql', graphql_app)
app.add_websocket_route(f'{api_settings.PREFIX}/graphql', graphql_app)


def get_response(data, response_format):
    if response_format == "text/xml" or response_format == "application/xml":
        root = ET.Element("data")
        for restaurant in data:
            item = ET.SubElement(root, "restaurant")
            for key, value in restaurant.items():
                elem = ET.SubElement(item, key)
                elem.text = str(value)
        response = ET.tostring(root, encoding="unicode")
        return Response(content=response, media_type="application/xml")
    else:
        return JSONResponse(content={"data": data})


@app.get("/")
def root():
    return {"message": f"Welcome to {api_settings.TITLE}"}


@app.get('/ciudad/{ciudad}/restaurante', responses={200: {'description': 'OK', "content": {"application/xml": {}}}})
def get_restaurantes(ciudad: str, Accept: str = Header(None)):
    restaurants = services.get_restaurants(ciudad)
    # print(restaurants)
    if (len(restaurants) == 0):
        return JSONResponse(content={
            "message": "No se encontraron restaurantes en la ciudad"
        }, status_code=404)
    return get_response(restaurants, Accept)


@app.get('/ciudad/{ciudad}/clima/manhana', responses={200: {'description': 'OK', "content": {"application/xml": {}}}})
def get_clima_manhana(ciudad: str, Accept: str = Header(None)):
    clima = services.getHourlyWeather(ciudad)
    # print(restaurants)
    if (len(clima) == 0):
        return JSONResponse(content={
            "message": "No se encontraron restaurantes en la ciudad"
        }, status_code=404)
    return get_response(clima, Accept)


@app.get('/ciudad/{ciudad}/clima/7dias', responses={200: {'description': 'OK', "content": {"application/xml": {}}}})
def get_clima_7dias(ciudad: str, Accept: str = Header(None)):
    clima = services.getDailyWeather(ciudad)
    # print(restaurants)
    if (len(clima) == 0):
        return JSONResponse(content={
            "message": "No se encontraron restaurantes en la ciudad"
        }, status_code=404)
    return get_response(clima, Accept)

@app.get('/cities', responses={200: {'description': 'OK', "content": {"application/xml": {}}}})
def get_cities_temp_date(temp: float, date: str, Accept: str = Header(None)):
    cities = services.getCitiesByTempDate(temperature=temp, date=date)
    return get_response(cities, Accept)

def run():
    uvicorn.run(app,
                host=api_settings.HOST,
                port=api_settings.PORT,
                )
