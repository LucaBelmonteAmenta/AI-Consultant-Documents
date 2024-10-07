import os

global APP_PATH
global init
# Take fixed file path, and not the relative file path
APP_PATH = os.path.dirname(os.path.realpath(__file__))
init = True