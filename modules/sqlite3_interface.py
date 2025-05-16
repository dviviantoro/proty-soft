import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()
cwd = os.getenv("CWD")

db_dir_path = f"{cwd}/assets/db"
 
def sqlite_create_table(table_name):
    # conn = sqlite3.connect('inventory.db')
    conn = sqlite3.connect(f"{db_dir_path}/inventory.db")
    cursor = conn.cursor()

    query_create = """
        CREATE TABLE IF NOT EXISTS {} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            fullname TEXT NOT NULL
        )
    """.format(table_name)
    cursor.execute(query_create)

    conn.commit()
    conn.close()

def sqlite_insert_data(db_name:str, table_name:str, data):
    # conn = sqlite3.connect(f"{db_name}.db")
    conn = sqlite3.connect(f"{db_dir_path}/{db_name}.db")
    cursor = conn.cursor()
    try:
        if table_name == "background":
            query_create = """
                CREATE TABLE IF NOT EXISTS {} (
                    id DATETIME PRIMARY KEY,
                    operator TEXT NOT NULL,
                    title TEXT NOT NULL,
                    location TEXT NOT NULL,
                    sensor_id TEXT NOT NULL
                )
            """.format(table_name)
            cursor.execute(query_create)

            insert_query = """
                INSERT INTO {} (id, operator, title, location, sensor_id)
                VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?)
            """.format(table_name)
            my_data = (data["operator"], data["title"], data["location"], data["sensor_id"])
        elif table_name == "calibration":
            query_create = """
                CREATE TABLE IF NOT EXISTS {} (
                    id DATETIME PRIMARY KEY,
                    operator TEXT NOT NULL,
                    title TEXT NOT NULL,
                    location TEXT NOT NULL,
                    sensor_id TEXT NOT NULL,
                    calibrator_id TEXT NOT NULL,
                    background_preset_timestamp TEXT NOT NULL
                )
            """.format(table_name)
            cursor.execute(query_create)

            insert_query = """
                INSERT INTO {} (id, operator, title, location, sensor_id, calibrator_id, background_preset_timestamp)
                VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?)
            """.format(table_name)
            my_data = (data["operator"], data["title"], data["location"], data["sensor_id"], data["calibrator_id"], data["background_preset_timestamp"])

        cursor.execute(insert_query, my_data)    
        conn.commit()
        conn.close()
        print(f"success insert data to {db_name} >> {table_name}")
    except Exception as e:
        print(e)


def sqlite_read_table(db_name:str, table_name:str):
    # conn = sqlite3.connect(f"{db_name}.db")
    conn = sqlite3.connect(f"{db_dir_path}/{db_name}.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM {}'.format(table_name))
    rows = cursor.fetchall()

    # for row in rows:
    #     print(row)
    conn.close()
    return rows

def sqlite_drop_table(db_name:str, table_name:str):
    conn = sqlite3.connect(f"{db_dir_path}/{db_name}.db")
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
    conn.commit()
    conn.close()