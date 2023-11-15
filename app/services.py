
from app.config.mongo import weather

######################################################
########### SHARDED MONGODB SERVICES##################
######################################################

def getCitiesByTempDate(temperature: float, date: str)->list[dict]:
    # Realiza la consulta a MongoDB
    query = {
        'fecha': date,
        'temperatura máxima': {'$gte': temperature, '$lt': temperature + 1.0}
    }

    result = list(weather.find(query))
    # devolver solo el 'nombre de ciudad' de cada documento en el resultado
    cities = []
    for doc in result:
        cities.append(doc['nombre de ciudad'])
    return cities
    