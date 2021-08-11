from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
from structs import *
from time import sleep
from random import randrange

fig = plt.figure()
ax = Axes3D(fig)

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
    c.set_facecolor(["Red", "White", "Orange", "Yellow", "Green", "Blue"])
    return c

def render(cube):
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
    plt.pause(.2)

def pause(x):
    plt.pause(x)



