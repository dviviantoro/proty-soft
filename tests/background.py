import theme
from nicegui import ui
from modules.sqlite3_interface import sqlite_read_table, sqlite_insert_data

def check_input(input, stepper):
    stepper.next() if input else ui.notify('plese input your data', type='warning')

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

def background_page() -> None:
    with theme.frame("Background Sampling Panel", 'You have to turn on all services'):
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
                location = generate_step(
                    stepper=stepper,
                    step_title="Location",
                    step_label="Name the location you are trying to sampling the background",
                    input_type="input"
                )
                sensor = generate_step(
                    stepper=stepper,
                    step_title="Sensor",
                    step_label="Select the sensor from the list below",
                    input_type="dropdown-sensor"
                )

                def grid_content():
                    grid_content = {
                        'defaultColDef': {'flex': 1},
                        'columnDefs': [
                            {'headerName': 'Parameter', 'field': 'param'},
                            {'headerName': 'Value', 'field': 'val'},
                        ],
                        'rowSelection': 'multiple',
                    }
                    return grid_content

                def update_grid_content(grid):
                    grid.options["rowData"] = [
                        {'param': 'Operator Name', 'val': operator.value},
                        {'param': 'Preset Title', 'val': title.value},
                        {'param': 'Location', 'val': location.value},
                        {'param': 'Sensor', 'val': generate_option("dropdown-sensor")[sensor.value]}
                    ]
                    grid.update()

                def struct_data():
                    data = {
                        "operator": operator.value,
                        "title": title.value,
                        "location": location.value,
                        "sensor_id": sensor.value
                    }
                    return data
                
                with ui.step("Review"):
                    with ui.row().classes("w-full place-content-center"):
                        ui.label("Please review your collected data before to start sampling").style('text-align: center;')
                    with ui.row().classes("w-full place-content-center"):
                        grid = ui.aggrid(grid_content()).classes('max-h-40')
                    with ui.row().classes("w-full place-content-center"):
                        with ui.stepper_navigation():
                            with ui.button(color="#FDE9A0", on_click=stepper.previous):
                                ui.label("Back").style("color: #494848")
                            with ui.button(color="#3874c8", on_click=lambda:update_grid_content(grid)):
                                ui.label("Reload Data").style("color: white")
                            with ui.button(color="#47C483", on_click=lambda:sqlite_insert_data("app_data", "background", struct_data())):
                                ui.label("Go Sampling").style("color: white")