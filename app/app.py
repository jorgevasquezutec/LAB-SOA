from fastapi import FastAPI, Header, Response
from starlette.middleware.cors import CORSMiddleware
from app.config.settings import api_settings
import uvicorn
from fastapi.responses import JSONResponse
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


@app.get('/cities', responses={200: {'description': 'OK', "content": {"application/xml": {}}}})
def get_cities_temp_date(temp: float, date: str, Accept: str = Header(None)):
    cities = services.getCitiesByTempDate(temperature=temp, date=date)
    return get_response(cities, Accept)

def run():
    uvicorn.run(app,
                host=api_settings.HOST,
                port=api_settings.PORT,
                )
