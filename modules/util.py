import redis
from tinydb import TinyDB, Query
import io
import matplotlib.pyplot as plt
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
    max_abs = 1

    if data_sensor.ndim == 1:
        count_pos = None
        count_neg = None
        avg_pos = None
        max_pos = None
        min_pos = None
        avg_neg = None
        max_neg = None
        min_neg = None
    else:
        pos = data_sensor[data_sensor[:, 1] > 0]
        neg = data_sensor[data_sensor[:, 1] < 0]

        count_pos = pos.shape[0]
        count_neg = neg.shape[0]

        avg_pos = round(np.mean(pos[:, 1]), 3)
        max_pos = round(np.max(pos[:, 1]), 3)
        min_pos = round(np.min(pos[:, 1]), 3)
        avg_neg = round(np.mean(neg[:, 1]), 3)
        max_neg = round(np.min(neg[:, 1]), 3)
        min_neg = round(np.max(neg[:, 1]), 3)

        if max_pos > abs(max_neg):
            max_abs = max_pos 
        else:
            max_abs = abs(max_neg)

    sentence = f"""
    metadata = {{
        "created": {formatted_datetime},
        "title": {title},
        "operator": {operator},
        "oscilloscope": {oscilloscope},
        "cycle": {cycle},
        "kV": {voltage},
        "positive": {{
            "count": {count_pos},
            "avg": {avg_pos},
            "max": {max_pos},
            "min": {min_pos}
        }},
        "negative": {{
            "count": {count_neg},
            "avg": {avg_neg},
            "max": {max_neg},
            "min": {min_neg}
        }}
    }}
"""
    sentence_json = {
        "created": formatted_datetime,
        "title": title,
        "operator": operator,
        "oscilloscope": oscilloscope,
        "cycle": int(cycle),
        "kV": float(voltage),
        "positive": {
            "count": count_pos,
            "avg": avg_pos,
            "max": max_pos,
            "min": min_pos
        },
        "negative": {
            "count": count_neg,
            "avg": avg_neg,
            "max": max_neg,
            "min": min_neg
        }
    }
    return sentence, sentence_json, max_abs

def create_matplotlib(sine, sensor, cycle, voltage):
    buffer_image = io.BytesIO()
    title = f"PRPD Charts for {cycle} Cycle at {voltage} kV"
    
    plt.figure(figsize=(10, 6))
    plt.plot(sine[:,0], sine[:,1], color='gray', linewidth=3)
    plt.plot(sensor[:,0], sensor[:,1], 'o', color='black', markersize=4)

    plt.xticks(np.arange(0, 361, 45), color='gray')
    plt.yticks(color='gray')
    plt.grid(True, which='both', axis='both', linestyle='--', linewidth=0.4, color='gray')
    plt.xlim(0, 360)

    plt.title(title)
    plt.xlabel("Degree", color='gray')
    plt.ylabel("Charge (pC)", color='gray')

    plt.savefig(buffer_image, format='jpg', dpi=300, bbox_inches='tight')
    plt.close()

    buffer_image.seek(0)
    return buffer_image.getvalue()

def insert_tiny(category, data):
    path = f"{json_db_path}/{category}.json"
    db = TinyDB(path)
    db.insert(data)