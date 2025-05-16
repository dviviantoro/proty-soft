from contextlib import contextmanager
from nicegui import ui, app
import os
from dotenv import load_dotenv
load_dotenv()
cwd = os.getenv('PARENT_PATH')
import sys
sys.path.insert(0, f'{cwd}/modules')

ui.button.default_props('no-caps')

ui.add_css("""
    .q-btn {
        box-shadow: none !important;
    }
""")

def logout() -> None:
    app.storage.user.clear()
    ui.navigate.to('/login')

@contextmanager
def frame(my_head: str, my_foot: str):
    with ui.column().classes('absolute-center items-center h-screen no-wrap p-9 w-full'):
        yield
    
    with ui.header().classes(replace='row items-center').style('display: flex; justify-content: space-between; width: 100%; background-color: #3874c8'):
        with ui.row().classes('items-center'):
            # ui.button(icon='photo_library', on_click=lambda:ui.navigate.back()).props('flat color=white')
            with ui.button(on_click=lambda:ui.navigate.back(), color="clear").props("flat"):
                ui.image("/Users/deny/proty02/assets/logo_proty.png").classes('rounded-full w-10 h-10')

            ui.label(my_head)
        # label_ping = ui.label('ping disini')
        with ui.button(icon='menu').props('flat color=white'):
            with ui.menu() as menu:
                ui.menu_item('Menu item 1', on_click=lambda:ui.navigate.to("/scope"))
                ui.separator()
                ui.menu_item('Close', menu.close)
                ui.menu_item('Logout', logout)
         
    with ui.footer().style('background-color: #3874c8'):
        # ui.label('FOOTER')
        with ui.row().style('display: flex; justify-content: space-between; width: 100%;'):
            ui.label(my_foot)
            ui.label("v25.2")

    # with ui.page_sticky(x_offset=20, y_offset=20):
    #     ui.button(on_click=lambda:ui.navigate.to('/passkey_page'), icon='tag').props('fab color=blue-5').set_visibility(passkey_bool)
        # my_button.set_visibility(False)