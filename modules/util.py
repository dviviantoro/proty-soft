import redis
from tinydb import TinyDB, Query
# from redis_interface import get_redis
from datetime import datetime
import numpy as np

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
json_db_path = "/Users/deny/proty02/assets/db"

def create_summary(last_data):
    created = "Bulan May"
    operator = last_data[0]
    title = last_data[1]
    oscilloscope = last_data[2]
    cycle = last_data[3]
    voltage = last_data[4]

    sentence = f"""
    metadata = {{
        "created": {created},
        "operator": {operator},
        "title": {title},
        "oscilloscope": {oscilloscope},
        "cycle": {cycle},
        "voltage": {voltage} kV
    }}
"""
    return sentence

def create_full_summary(data_sensor):
    now = datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    operator = r.get("operator")
    title = r.get("title")
    oscilloscope = r.get("oscilloscope")
    cycle = r.get("cycle")
    voltage = r.get("voltage")

    if data_sensor.ndim == 1:
        avg_pos = None
        max_pos = None
        min_pos = None
        avg_neg = None
        max_neg = None
        min_neg = None
    else:
        pos = data_sensor[data_sensor[:, 1] > 0]
        neg = data_sensor[data_sensor[:, 1] < 0]

        avg_pos = np.mean(pos[:, 1])
        max_pos = np.max(pos[:, 1])
        min_pos = np.min(pos[:, 1])
        avg_neg = np.mean(neg[:, 1])
        max_neg = np.min(neg[:, 1])
        min_neg = np.max(neg[:, 1])

    sentence = f"""
    metadata = {{
        "created": {formatted_datetime},
        "title": {title},
        "operator": {operator},
        "oscilloscope": {oscilloscope},
        "cycle": {cycle},
        "voltage": {voltage} kV
        "positive": {{
            "avg": {avg_pos},
            "max": {max_pos},
            "min": {min_pos}
        }},
        "negative": {{
            "avg": {avg_neg},
            "max": {max_neg},
            "min": {min_neg}
        }}
    }}
"""
    return sentence

def insert_tiny(category, data):
    path = f"{json_db_path}/{category}.json"
    db = TinyDB(path)
    db.insert(data)