import multiprocessing
multiprocessing.set_start_method("spawn", force=True)
import os

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from nicegui import app, ui
from dotenv import load_dotenv

import pages.home as home_page
import theme
import all_pages

load_dotenv()
cwd = os.getenv('PARENT_PATH')

unrestricted_page_routes = {'/login'}

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get('authenticated', False):
            if not request.url.path.startswith('/_nicegui') and request.url.path not in unrestricted_page_routes:
                app.storage.user['referrer_path'] = request.url.path  # remember where the user wanted to go
                return RedirectResponse('/login')
        return await call_next(request)

app.add_middleware(AuthMiddleware)

@ui.page('/')
def main_page() -> None:
    def logout() -> None:
        app.storage.user.clear()
        ui.navigate.to('/login')

    with theme.frame("Proty-Soft, Phase Resolved Partial Discharge Auto-Charts", 'Version 03.25.1'):
        home_page.content()

all_pages.create()

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(storage_secret='THIS_NEEDS_TO_BE_CHANGED', favicon="🚀", title="Proty02", show=False, port=9000)
