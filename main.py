from structs import *
from plotter import render
from time import sleep
from random import randrange

cube = Cube(3)
render(cube)

for i in range(1000):
    for j in range(1000):
        ai = randrange(len(ACTIONS))
        cube = cube.apply(ACTIONS[ai])
    render(cube)