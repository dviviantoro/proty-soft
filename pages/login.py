import os
from nicegui import ui, app
from typing import Optional
from fastapi.responses import RedirectResponse

from dotenv import load_dotenv
load_dotenv()
cwd = os.getenv('CWD')

# in reality users passwords would obviously need to be hashed
passwords = {'user1': 'pass1', 'user2': 'pass2'}

# app.add_static_files(cwd + '/assets', cwd + '/assets')
# app.add_static_files(f'{cwd}/assets', f'{cwd}/assets')
lottie_player = cwd + '/assets/lottie/player.js'
# src_lottie_camera = cwd + '/assets/lottie/whale.json'
# src_lottie_camera = '/Users/deny/proty02/assets/lottie/whale.json'

@ui.page('/login')
def login_page() -> Optional[RedirectResponse]:
    def try_login() -> None:  # local function to avoid passing username and password as arguments
        if passwords.get(username.value) == password.value:
            app.storage.user.update({'username': username.value, 'authenticated': True})
            ui.navigate.to(app.storage.user.get('referrer_path', '/'))  # go back to where the user wanted to go
        else:
            ui.notify('Wrong username or password', color='negative')

    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')
    
    # with ui.row().classes('w-full place-content-center'):
    # ui.add_body_html(f'<script src={lottie_player}></script>')
        # with ui.element('div').classes('absolute-center'):
        #     with ui.row().classes('grid grid-cols-12 w-full gap-4'):
    # ui.html(f'<lottie-player src="{src_lottie_camera}" loop autoplay />').classes('w-full')

    # ui.add_body_html('<script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>')
    # src = 'https://assets1.lottiefiles.com/datafiles/HN7OcWNnoqje6iXIiZdWzKxvLIbfeCGTmvXmEm1h/data.json'
    # ui.html(f'<lottie-player src="{src}" loop autoplay />').classes('w-full')


    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        ui.button('Log in', on_click=try_login)
    return None