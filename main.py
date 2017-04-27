import pygame as pg
import sys
from app import App

"""Fighting game made by Bennett Rasmussen spring 2017"""

screen = pg.display.set_mode((1500, 600))

App().main_loop()
pg.quit()
sys.exit()
