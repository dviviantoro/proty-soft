def create_dict_stream(data_stream):
    dictionary = {
        "tooltip": {"trigger": "item"},
        "legend": {'textStyle': {'color': 'gray'}},
        "xAxis": {"type": "value", "name": "Time"},
        "yAxis": {"type": "value", "name": "Voltage (mV)"},
        "grid": {
            "top": 40,
            "bottom": 40,
            "left": 60,
            "right": 60
        },
        "series": [
            {
                "name": "Streaming",
                "type": "scatter",
                "data": data_stream,
                "itemStyle": {
                    "color": '#e63946'
                }
            }
        ]
    }
    return dictionary

def create_dict_prpd(data_sine, data_sensor):
    dictionary = {
        "tooltip": {"trigger": "item"},
        "legend": {'textStyle': {'color': 'gray'}},
        "xAxis": {"type": "value", "name": "Deg", "interval": 45, "max": 360},
        "yAxis": {"type": "value", "name": "Voltage (mv)"},
        "grid": {
            "top": 40,
            "bottom": 40,
            "left": 60,
            "right": 60
        },
        "series": [
            {
                "name": "Phase Ref",
                "type": "line",
                "data": data_sine,
                "itemStyle": {
                    "color": '#3a86ff'
                }
            },
            {
                "name": "(+)Sensor",
                "type": "scatter",
                "data": data_sensor,
                "itemStyle": {
                    "color": '#e63946'
                }
            }
        ]
    }
    return dictionary

def create_dict_prpd_pos_neg(data_sine, data_sensor_pos, data_sensor_neg):
    dictionary = {
        "tooltip": {"trigger": "item"},
        "legend": {'textStyle': {'color': 'gray'}},
        "xAxis": {"type": "value", "name": "Deg"},
        "yAxis": {"type": "value", "name": "Charge (pC)"},
        "grid": {
            "top": 40,
            "bottom": 40,
            "left": 60,
            "right": 60
        },
        "series": [
            {
                "name": "Phase Ref",
                "type": "line",
                "data": data_sine,
                "itemStyle": {
                    "color": '#3a86ff'
                }
            },
            {
                "name": "(+)Sensor",
                "type": "scatter",
                "data": data_sensor_pos,
                "itemStyle": {
                    "color": '#e63946'
                }
            },
            {
                "name": "(-)Sensor1",
                "type": "scatter",
                "data": data_sensor_neg,
                "itemStyle": {
                    "color": '#3d348b'
                }
            }
        ]
    }
    return dictionary

def create_dict_historical(title, yAxis, data):
    dictionary = {
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item"},
        "xAxis": {"type": "time", "name": "Time"},
        "yAxis": {"type": "value", "name": yAxis},
        "dataset": {"source": data, "dimensions": ['timestamp', 'pos', 'neg']},
        "grid": {
            "top": 40,
            "bottom": 40,
            "left": 60,
            "right": 60
        },
        "series": [
            {
                "name": "Positive",
                "type": "line",
                "encode": {
                    "x": "timestamp",
                    "y": "pos"
                }
            },
            {
                "name": "Negative",
                "type": "line",
                "encode": {
                    "x": "timestamp",
                    "y": "neg"
                }
            },

        ]
    }
    return dictionary

def create_dict_counter_background(title, yAxisLabel, data):
    dictionary = {
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item"},
        "xAxis": {"type": "value", "name": "Count"},
        "yAxis": {"type": "value", "name": yAxisLabel},
        "dataset": {"source": data, "dimensions": ['count', 'pos', 'neg']},
        "grid": {
            "top": 40,
            "bottom": 40,
            "left": 60,
            "right": 60
        },
        "series": [
            {
                "name": "Positive",
                "type": "line",
                "encode": {
                    "x": "count",
                    "y": "pos"
                }
            },
            {
                "name": "Negative",
                "type": "line",
                "encode": {
                    "x": "count",
                    "y": "neg"
                }
            },

        ]
    }
    return dictionary
