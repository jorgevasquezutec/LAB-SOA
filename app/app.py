from fastapi import FastAPI, Request,Header, Response
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

@app.get('/ciudad/{ciudad}/restaurante', responses={200:{'description': 'OK', "content": {"application/xml": {}}}})
def get_restaurantes(ciudad: str, Accept: str = Header(None)):
    restaurants = services.get_restaurants(ciudad)
        # print(restaurants)
    if(len(restaurants) == 0):
        return JSONResponse(content={
            "message": "No se encontraron restaurantes en la ciudad"
        }, status_code=404)
    return get_response(restaurants, Accept)

@app.get('/ciudad/{ciudad}/clima/manhana',responses={200:{'description': 'OK', "content": {"application/xml": {}}}})
def get_clima_manhana(ciudad: str, Accept: str = Header(None)):
    clima = services.getHourlyWeather(ciudad)
    # print(restaurants)
    if(len(clima) == 0):
        return JSONResponse(content={
            "message": "No se encontraron restaurantes en la ciudad"
        }, status_code=404)
    return get_response(clima, Accept)

@app.get('/ciudad/{ciudad}/clima/7dias',responses={200:{'description': 'OK', "content": {"application/xml": {}}}})
def get_clima_7dias(ciudad: str, Accept: str = Header(None)):
    clima = services.getDailyWeather(ciudad)
    # print(restaurants)
    if(len(clima) == 0):
        return JSONResponse(content={
            "message": "No se encontraron restaurantes en la ciudad"
        }, status_code=404)
    return get_response(clima, Accept)

def run():
    uvicorn.run(app,
                host=api_settings.HOST,
                port=api_settings.PORT,
                )
