from collections import defaultdict
from structs import *
import random


def calc_edge_orientations(actions):
    cube = Cube(3).sub_cube(lambda c: c.actual_location.x == 1 and c.actual_location.y == 1 and c.actual_location.z == 0)
    cube = Cube(3).sub_cube(edge)
    peice_orientations = defaultdict(set)

    while True:
        for i in range(100):
            for b in cube.blocks:
                os = b.orientations
                peice_orientations[b.solved_location].add(tuple(os))

            cube = cube.apply(random.choice(actions))
        if all(len(v) == 12 for v in peice_orientations.values()):
            return peice_orientations

def calc_corner_orientations(actions):
    cube = Cube(3).sub_cube(lambda c: c.actual_location.x == 1 and c.actual_location.y == 1 and c.actual_location.z == 1)
    o_set = set()

    while len(o_set) < 8:
        os = cube.blocks[0].orientations
        o_set.add(tuple([os[0], os[1]]))

        cube = cube.apply(random.choice(actions))
    return o_set



if __name__ == "__main__":
    actions = QUARTER_X + QUARTER_Y + HALF_FACE
    os = calc_edge_orientations(actions)
    print(len(os))

    # actions = QUARTER_X + QUARTER_Y + HALF_Z
    # os = calc_edge_orientations(actions)
    # print(os)

    # actions = QUARTER_X + HALF_Y + HALF_Z
    # os = calc_corner_orientations(actions)
    # print(os)
