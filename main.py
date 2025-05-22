import pygame as py
import os 
import sys
import time as ti 


py.init()
running = True 

while running:
    for event in py.event.type:
        if event.type == py.QUIT:
            running  = False
