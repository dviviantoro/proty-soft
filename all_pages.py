from nicegui import ui
from pages.login import login_page
from pages.result import result_page
# from pages.calibration import calibration_page
# from pages.acquisition import acquisition_page
# from pages.scope import scope_page

# from pages.scope_background import scope_background_page

def create() -> None:
    ui.page('/login')(login_page)
    ui.page('/result')(result_page)

    # ui.page("/background")(background_page)
    # ui.page("/calibration")(calibration_page)
    # ui.page("/acquisition")(acquisition_page)
    # ui.page("/scope")(scope_page)
    # ui.page("/scpbgn")(scope_background_page)

if __name__ == '__main__':
    create()