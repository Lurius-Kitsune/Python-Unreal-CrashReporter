from io import BytesIO
from app import App
import logging

def Main():
    _logger : logging.Logger
    _appInstance = App()
    _appInstance.run()


Main()