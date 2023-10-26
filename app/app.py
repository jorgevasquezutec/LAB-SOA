from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from app.config.settings import api_settings
import uvicorn
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from app.constants.values import LOG_API_PATHS
import requests
import concurrent.futures


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


@app.get("/")
def root():
    return {"message": f"Welcome to {api_settings.TITLE}"}


def fetch_data(api_url):
    response = requests.get(api_url)
    return response.json()


# @app.get("/search/{name}")
# # @log_request()
# def root(name: str):
#     try:
#         name = name.lower()

#         api_urls = [
#             f'{api_settings.API_GATEWAY}poke_api/search/{name}',
#             f'{api_settings.API_GATEWAY}poke_stats/search/{name}',
#             f'{api_settings.API_GATEWAY}poke_images/search/{name}',
#         ]
#         # print(api_urls)

#         with concurrent.futures.ThreadPoolExecutor() as executor:
#             results = list(executor.map(fetch_data, api_urls))

#         return {"data": results}

#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail=str(e))


def run():
    uvicorn.run(app,
                host=api_settings.HOST,
                port=api_settings.PORT,
                )
