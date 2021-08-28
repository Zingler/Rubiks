from structs import *
import random


def calc_edge_orientations(actions):
    cube = Cube(3).sub_cube(lambda c: c.actual_location.x == 1 and c.actual_location.y == 1 and c.actual_location.z == 0)
    o_set = set()

    while len(o_set) < 12:
        os = cube.blocks[0].orientations
        o_set.add(tuple([os[0], os[1]]))

        cube = cube.apply(random.choice(actions))
    return o_set

def calc_corner_orientations(actions):
    cube = Cube(3).sub_cube(lambda c: c.actual_location.x == 1 and c.actual_location.y == 1 and c.actual_location.z == 1)
    o_set = set()

    while len(o_set) < 8:
        os = cube.blocks[0].orientations
        o_set.add(tuple([os[0], os[1]]))

        cube = cube.apply(random.choice(actions))
    return o_set



if __name__ == "__main__":
    actions = HALF_FACE
    os = calc_edge_orientations(actions)
    print(len(os))

    # actions = QUARTER_X + QUARTER_Y + HALF_Z
    # os = calc_edge_orientations(actions)
    # print(os)

    # actions = QUARTER_X + HALF_Y + HALF_Z
    # os = calc_corner_orientations(actions)
    # print(os)
