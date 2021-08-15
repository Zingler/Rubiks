import queue
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, line_2d_to_3d
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from structs import *
from time import sleep
from random import randrange

import multiprocessing as mp
from multiprocessing import Process, Queue

def face():
    return [Vector(.5,.5,.5),Vector(.5,-.5,.5),Vector(.5,-.5,-.5), Vector(.5,.5,-.5)]
def f_to_v(face):
    return [[v.x,v.y,v.z] for v in face]
def rX(face):
    return map(Vector.rotateX, face)
def rY(face):
    return map(Vector.rotateY, face)
def rZ(face):
    return map(Vector.rotateZ, face)

def condense(p):
    return [x-[-.5,.5][x>0] for x in p]

FACE_TEMPLATE = [face(), rY(face()), rY(rY(face())), rY(rY(rY(face()))), rZ(face()), rZ(rZ(rZ(face())))]

def block_to_3dcollection(block, size) :
    faces = [face(), rY(face()), rY(rY(face())), rY(rY(rY(face()))), rZ(face()), rZ(rZ(rZ(face())))]
    o = block.orientations
    rotor = Matrix.rotor(*o)
    faces = [[(rotor * v) + block.actual_location for v in f] for f in faces]

    verts = [f_to_v(f) for f in faces]
    if size % 2 == 0:
        verts = [[condense(p) for p in v] for v in verts]
    c = Poly3DCollection(verts, closed=True)
    c.set_facecolor(["Blue", "Yellow", "Orange", "White", "Green", "Red"])
    return c


def PlotProcess(cube_queue):
    fig = plt.figure()
    ax = Axes3D(fig)

    i = -1.5
    for si in range(4):
        j = -1.5
        for sj in range(4):
            ax.plot([i,i],[j,j],zs=[-1.5,1.5], color="grey")
            ax.plot([i,i],[-1.5,1.5],zs=[j,j], color="grey")
            ax.plot([-1.5,1.5],[i,i],zs=[j,j], color="grey")
            j += 1
        i += 1

    def check_queue():
        cube = None
        try:
            while True:
                cube = cube_queue.get(block=False)
        except queue.Empty:
            if not cube:
                return
        size = cube.size

        plt.xlim([-(size-1), size-1])
        plt.ylim([-(size-1), size-1])
        ax.set_zlim(-(size-1), size-1)
        plt.grid(False)
        plt.axis('off')
        ax.collections = []
        for b in cube.blocks:
            ax.add_collection3d(block_to_3dcollection(b, size))
        plt.draw()

    timer = fig.canvas.new_timer(interval=200)
    timer.add_callback(check_queue)
    timer.start()

    plt.show()

def start_plotter():
    def render(cube):
        queue.put(cube)

    queue = mp.Queue()
    mp.Process(target=PlotProcess, args=[queue], daemon=False).start()

    return render



