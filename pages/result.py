import io
import theme
from nicegui import ui
from modules.dsp import *
from modules.dictionary import *
import pandas as pd
import asyncio
import random
from datetime import datetime
import os
import sys
from multiprocessing import shared_memory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
from modules.sqlite3_interface import sqlite_read_table
from modules.redis_interface import get_redis
from modules.util import create_full_summary

# def create_file_and_download():
def create_csv_from_numpy(target, array):
    # np.savetxt(buffer, arr, delimiter=",", fmt="%d")
    np.savetxt(target, array, delimiter=",", fmt="%d")

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

    buffer_data_sensor = io.StringIO()

    def update_prpd(chart, code, bgn_pos, bgn_neg, cycle):
        if bgn_pos == None : bgn_pos = 0
        if bgn_neg == None : bgn_neg = 0
        data_sensor = filter_noise_and_align(copied_source, copied_sensor, bgn_pos, bgn_neg, cycle)
        data_sensor = filter_degree(data_sensor, degStartPos.value, degEndPos.value, degStartNeg.value, degEndNeg.value)

        columns = ['time', 'value']
        df = pd.DataFrame(data_sensor, columns=columns)
        df.to_csv(buffer_data_sensor, index=False)
        buffer_data_sensor.seek(0)
        
        np.savetxt(buffer_data_sensor, data_sensor, delimiter=",", fmt="%.2f")

        code.set_content(create_full_summary(data_sensor))
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
                        data_sine = generate_sine()
                        """
                        data_sensor = filter_and_align(copied_source, copied_sensor, 0.005, -0.005)
                        data_sensor[:, 0] += 1
                        pos = data_sensor[data_sensor[:, 1] > 0]
                        neg = data_sensor[data_sensor[:, 1] < 0]
                        """
                        chart_prpd = ui.echart(options=create_dict_prpd(data_sine, [])).classes('h-[640px] w-full')

            with ui.card().classes('no-shadow col-start-9 col-span-4 size-full'):
                ui.label('Panel Control')
                summary = ui.code(create_full_summary(copied_sensor)).classes('w-full')
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
                    ui.button("check", color="#47C483", on_click=lambda: update_prpd(chart_prpd, summary, bgn_pos.value, bgn_neg.value, int(metadata["cycle"])))
                    ui.button("download", color="#F3C623", on_click=lambda: ui.download.file(buffer_data_sensor))
                    # ui.button("download", color="#F3C623", on_click=lambda: ui.download.content(buffer_data_sensor, 'test.csv'))
