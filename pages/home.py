import os
from nicegui import ui, app, events
from modules.sqlite3_interface import sqlite_read_table
import pandas as pd
import numpy as np
from io import StringIO
from multiprocessing import shared_memory
from modules.util import create_summary
from modules.redis_interface import set_redis

def source_csv_file_handler(e: events.UploadEventArguments):
    with StringIO(e.content.read().decode("utf-8")) as f:
        df = pd.read_csv(f)
    result = df["Value"].to_numpy()
    try:
        shm = shared_memory.SharedMemory(create=True, size=result.nbytes, name="source")
        shared_data = np.ndarray(result.shape, dtype=result.dtype, buffer=shm.buf)
        shared_data[:] = result[:]
    except Exception as e:
        print(e)
        shared_data[:] = result[:]

def sensor_csv_file_handler(e: events.UploadEventArguments):
    with StringIO(e.content.read().decode("utf-8")) as f:
        df = pd.read_csv(f)
    result = df["Value"].to_numpy()
    try:
        shm = shared_memory.SharedMemory(create=True, size=result.nbytes, name="sensor")
        shared_data = np.ndarray(result.shape, dtype=result.dtype, buffer=shm.buf)
        shared_data[:] = result[:]
    except Exception as e:
        print(e)
        shared_data[:] = result[:]
    
def check_input(input, stepper):
    stepper.next() if input else ui.notify('please input your data', type='warning')

def generate_option(input_type):
    option = {}
    dropdown_data = input_type.split("-")[1]
    datas = sqlite_read_table("inventory", dropdown_data)
    for data in datas:
        option[data[0]] = data[1] + " from " + data[3]
    return option

def generate_step(stepper, step_title:str, step_label:str, input_type:str):
    with ui.step(step_title):
        with ui.row().classes("w-full place-content-center"):
            ui.label(step_label).style('text-align: center;')
        with ui.row().classes("w-full place-content-center"):
            if input_type == "input":
                my_input = ui.input(placeholder='type here').props('rounded outlined dense')
            else:
                my_input = ui.select(generate_option(input_type))
        with ui.row().classes("w-full place-content-center"):
            with ui.stepper_navigation():
                if step_title != "Operator":
                    with ui.button(color="#FDE9A0", on_click=stepper.previous):
                        ui.label("Back").style("color: #494848")
                with ui.button(color="#47C483", on_click=lambda:check_input(my_input.value, stepper)):
                    ui.label("Next").style("color: white")
    return my_input

def check_uploaded_csv(stepper):
    try:
        shared_memory.SharedMemory(name='source')
        shared_memory.SharedMemory(name='sensor')
        stepper.next()
    except Exception as e:
        ui.notify('plese input your data', type='warning')

def go_process(data):
    keys = ["operator", "title", "oscilloscope", "cycle", "voltage"]
    for i in range(5):
        set_redis(keys[i], data[i])

    ui.navigate.to("/result")

@ui.page('/')
def content() -> None:
    with ui.element('div').classes('grid-cols-12 absolute-center gap-10'):
        with ui.stepper().props('horizontal') as stepper:
            operator = generate_step(
                stepper=stepper,
                step_title="Operator",
                step_label="Write your name to make the next step easier",
                input_type="input"
            )
            title = generate_step(
                stepper=stepper,
                step_title="Title",
                step_label="Name the title of background sampling process",
                input_type="input"
            )
            with ui.step("Metadata"):
                with ui.row().classes("w-full place-content-center"):
                    ui.label("Fill detail required data below").style('text-align: center;')

                with ui.row().classes("w-full place-content-center"):
                    oscilloscope_option = {}
                    datas = sqlite_read_table("inventory", "oscilloscope")
                    for data in datas:
                        oscilloscope_option[data[0]] = data[1]
                    oscilloscope = ui.select(options = oscilloscope_option, with_input=True, label="Oscilloscope option")
                    cycle = ui.select([1,2,3,4,5,6,7,8], with_input=True, label="Number of cycle")
                    voltage = ui.input(placeholder="Voltage in kV")

                with ui.row().classes("w-full place-content-center"):
                    with ui.stepper_navigation():
                        with ui.button(color="#FDE9A0", on_click=stepper.previous):
                            ui.label("Back").style("color: #494848")
                        with ui.button(color="#47C483", on_click=lambda: stepper.next() if oscilloscope.value and cycle.value else ui.notify('plese input your data', type='warning')):
                            ui.label("Next").style("color: white")
            
            with ui.step("Upload data"):
                with ui.row().classes("w-full place-content-center"):
                    ui.label("Fill detail required data below").style('text-align: center;')

                with ui.row().classes("w-full place-content-center"):
                    source_upload = ui.upload(label="Upload csv source here", on_upload=source_csv_file_handler).props("accept=.csv").classes("max-w-full")
                    sensor_upload = ui.upload(label="Upload csv sensor here", on_upload=sensor_csv_file_handler).props("accept=.csv").classes("max-w-full")

                with ui.row().classes("w-full place-content-center"):
                    with ui.stepper_navigation():
                        with ui.button(color="#FDE9A0", on_click=stepper.previous):
                            ui.label("Back").style("color: #494848")
                        with ui.button(color="#47C483", on_click=lambda: check_uploaded_csv(stepper)):
                            ui.label("Next").style("color: white")            

            with ui.step("Review"):
                with ui.row().classes("w-full place-content-center"):
                    ui.label("Please review your collected data before to start sampling").style('text-align: center;')
                with ui.row().classes("w-full place-content-center"):
                    summary = ui.code(create_summary([None, None, None, None, None])).classes('w-full')
                with ui.row().classes("w-full place-content-center"):
                    with ui.stepper_navigation():
                        with ui.button(color="#FDE9A0", on_click=stepper.previous):
                            ui.label("Back").style("color: #494848")
                        with ui.button(color="#3874c8",on_click=lambda:summary.set_content(create_summary([operator.value,title.value,oscilloscope_option[oscilloscope.value],cycle.value,voltage.value]))):
                            ui.label("Reload Data").style("color: white")
                        with ui.button(color="#47C483", on_click=lambda:go_process([operator.value,title.value,oscilloscope_option[oscilloscope.value],cycle.value,voltage.value])):
                            ui.label("Go Charting").style("color: white")
    