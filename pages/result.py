import io
import theme
from nicegui import ui
from modules.dsp import *
from modules.dictionary import *
from zipfile import ZipFile
import pandas as pd
import asyncio
import json
from datetime import datetime
import os
import sys
from multiprocessing import shared_memory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
from modules.sqlite3_interface import sqlite_read_table
from modules.redis_interface import get_redis
from modules.util import create_full_summary, create_matplotlib

def create_csv_buffer(name, array):
    df = pd.DataFrame(array, columns=['x', 'y'])
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return name, buffer.getvalue().encode('utf-8')  # name and bytes

def result_page() -> None:
    metadata = {}
    keys = ["operator", "title", "oscilloscope", "cycle", "voltage"]
    for i in keys:
        metadata[i] = get_redis(i)

    shm_source = shared_memory.SharedMemory(name='source')
    shared_source = np.ndarray((100000,), dtype=np.float64, buffer=shm_source.buf)
    copied_source = shared_source.copy()
    shm_sensor = shared_memory.SharedMemory(name='sensor')
    shared_sensor = np.ndarray((100000,), dtype=np.float64, buffer=shm_sensor.buf)
    copied_sensor = shared_sensor.copy()

    buffer_zip = io.BytesIO()

    def update_prpd(chart, code):
        bgn_pos_val = bgn_pos.value 
        bgn_neg_val = bgn_neg.value 

        if bgn_pos_val == None : bgn_pos_val = 0
        if bgn_neg_val == None : bgn_neg_val = 0
        data_sensor = filter_noise_and_align(copied_source, copied_sensor, bgn_pos_val, bgn_neg_val, int(metadata["cycle"]))
        data_sensor = filter_degree(data_sensor, degStartPos.value, degEndPos.value, degStartNeg.value, degEndNeg.value)
        data_sensor = apply_calibration(data_sensor, a.value, c.value)

        code_sentece, json_sentence, max_abs = create_full_summary(data_sensor)
        data_sine = generate_sine(amplitude=max_abs*1.4)

        buffer_metadata = io.StringIO()
        json.dump(json_sentence, buffer_metadata)

        arrays = {
            'sensor.csv': data_sensor,
            'source.csv': data_sine
        }
        files = [create_csv_buffer(name, arr) for name, arr in arrays.items()]
        
        with ZipFile(buffer_zip, 'w') as zip_file:
            for filename, content in files:
                zip_file.writestr(filename, content)
            zip_file.writestr("chart.jpg", create_matplotlib(data_sine, data_sensor, metadata["cycle"], metadata["voltage"]))
            zip_file.writestr("metadata.json", buffer_metadata.getvalue())
        buffer_zip.seek(0)

        code.set_content(code_sentece)
        chart.options['series'][0]['data'] = data_sine
        chart.options['series'][1]['data'] = data_sensor
        chart.update()

    with theme.frame("Oscilloscope Panel", "OK!"):
        with ui.element('div').classes('grid grid-cols-12 w-full gap-5 mt-16 mb-16'):
            with ui.element('div').classes('col-start-1 col-span-8 size-full'):
                with ui.tabs().classes('w-full') as tabs:
                    tab_raw = ui.tab('Raw Data')
                    tab_prpd = ui.tab('Phase-Resolved')
                with ui.tab_panels(tabs, value=tab_prpd).classes('w-full'):
                    with ui.tab_panel(tab_raw):
                        with ui.matplotlib(figsize=(18, 12)).figure as fig_source:
                            x = np.arange(len(copied_source))
                            ax = fig_source.gca()
                            ax.plot(x, copied_source, '-g')
                            ax.plot(x, copied_sensor, '-b')
                    with ui.tab_panel(tab_prpd):
                        data_sine = generate_sine(30)
                        chart_prpd = ui.echart(options=create_dict_prpd(data_sine, [])).classes('h-[640px] w-full')

            with ui.card().classes('no-shadow col-start-9 col-span-4 size-full'):
                ui.label('Panel Control')
                summary = ui.code(create_full_summary(copied_sensor)[0]).classes('w-full')
                with ui.row().classes("w-full place-content-center grid grid-cols-12"):
                    bgn_pos = ui.number(label='Noise Positive in mV', precision=4).props('clearable').classes('col-start-1 col-span-6 size-full')
                    bgn_neg = ui.number(label='Noise Negative in mV', precision=4).props('clearable').classes('col-start-7 col-span-6 size-full')
                with ui.row().classes("w-full place-content-center grid grid-cols-12"):
                    degStartPos = ui.number(label='degStartPos').classes('col-start-1 col-span-3 size-full')
                    degEndPos = ui.number(label='degEndPos').classes('col-start-4 col-span-3 size-full')
                    degStartNeg = ui.number(label='degStartNeg').classes('col-start-7 col-span-3 size-full')
                    degEndNeg = ui.number(label='degEndNeg').classes('col-start-10 col-span-3 size-full')
                with ui.row().classes("w-full place-content-center grid grid-cols-12"):
                    a = ui.number(label='Calibration (Ax)').classes('col-start-3 col-span-4 size-full')
                    c = ui.number(label='Calibration (C)').classes('col-start-7 col-span-4 size-full')

                with ui.row().classes("w-full place-content-center"):
                    ui.button("check", color="#47C483", on_click=lambda: update_prpd(chart_prpd, summary))
                    ui.button("download", color="#F3C623", on_click=lambda: ui.download.content(buffer_zip.getvalue(), filename=f'proty_result_{metadata["title"]}.zip'))
    with ui.page_sticky(x_offset=18, y_offset=18):
        ui.button(icon='sms', on_click=lambda: ui.navigate.to('https://wa.me/6285741311479')).props('fab color=green')