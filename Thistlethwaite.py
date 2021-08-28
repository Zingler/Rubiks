from patterndb import CornerOrientationAxisKeyGenerator, EdgeSliceKeyGen, OrientationKeyGenerator, build_db, corner_perm_db
from structs import *
from astar import *
from orientationcalc import calc_corner_orientations
import sys


class Group2To3Problem(Problem):
    def __init__(self, cube):
        self._initial_state = cube
        self._actions = QUARTER_X + HALF_FACE
        model_cube = Cube(3)
        edge_cube = model_cube.sub_cube(edge)
        corner_cube = model_cube.sub_cube(corner)
        self._dbs = [
            build_db("2to3EdgeSlice", edge_cube, 9, QUARTER_X + HALF_FACE, pattern_db_options={
            "match_on_solved_location": False,
            "key_generators": [EdgeSliceKeyGen]
        }),
            build_db("CornerOrientationAxis", corner_cube, 6, QUARTER_X + HALF_FACE, pattern_db_options={
            "match_on_solved_location": False,
            "key_generators": [OrientationKeyGenerator]
        }),
        ]
        self.corner_perm_db = corner_perm_db()

    def initial_state(self):
        return self._initial_state

    def goal_test(self, state):
        c = self.incorrect_blocks(state)
        return c == 0 and self.corner_perm_db.contains_cube(state)

    def actions(self, node):
        return filter_actions(self._actions, node.action)

    def apply_action(self, state, action):
        return state.apply(action), 1

    def heuristic(self, state):
        db_lookup = max([db.get_from_cube(state) for db in self._dbs])
        value = max(self.incorrect_blocks(state) / 8, db_lookup)
        if value == 0:
            value = max(value, 1-int(self.corner_perm_db.contains_cube(state)))
        return value

    def incorrect_blocks(self, state):
        c = 0
        for b in state.blocks:
            orbit = b.correct_orbit() and b.correct_slice()
            orientations = abs(b.orientations[0].x) == 1
            c += not orientations or not orbit
        return c


class Group3ToFinalProblem(Problem):
    def __init__(self, cube):
        self._initial_state = cube
        self._actions = HALF_FACE
        model_cube = Cube(3).sub_cube_from_cube(cube)
        edge_cube = model_cube.sub_cube(edge)
        corner_cube = model_cube.sub_cube(corner)
        self._dbs = [build_db("finaledge", edge_cube, 9, HALF_FACE),
                     build_db("finalcorner", corner_cube, 9, HALF_FACE),
                     build_db("finalfull", model_cube, 8, HALF_FACE)]

    def initial_state(self):
        return self._initial_state

    def goal_test(self, state):
        return state.solved()

    def actions(self, node):
        return filter_actions(self._actions, node.action)

    def apply_action(self, state, action):
        return state.apply(action), 1

    def heuristic(self, state):
        db_lookup = max([db.get_from_cube(state) for db in self._dbs])
        return max(state.half_turn_distance() / 8, db_lookup)


if __name__ == "__main__":
    from plotter import start_plotter
    from time import sleep
    from random import randrange
    from astar import search
    from orientationsolver import OrientationProblem
    from cubesolver import CubeProblem

    render = start_plotter()

    original = Cube(3)
    turns = 200

    for i in range(turns):
        original = original.apply(random.choice(QUARTER_X + HALF_FACE))
        # original = original.apply(random.choice(HALF_FACE))

    total_actions = []

    def callback(status):
        print(status, end='\r')
        sys.stdout.flush()

        render(status["state"])
        pass

    running = original

    states, actions = search(Group2To3Problem(running), callback=callback, callback_freq=100)

    print(f'Solved step in {len(actions)-1} turns')
    total_actions.extend(actions[1:])
    for a in actions[1:]:
        running = running.apply(a)

    half_turn_cube = running.sub_cube(lambda b: b.solved_location.x == 1 or b.solved_location.y == 1 or b.solved_location.z == 1)
    states, actions = search(Group3ToFinalProblem(half_turn_cube), callback=callback, callback_freq=100)

    print(f'Solved step in {len(actions)-1} turns')
    total_actions.extend(actions[1:])
    for a in actions[1:]:
        running = running.apply(a)

    print(f"Full solve in {len(total_actions)} turns")

    for i in range(20):
        current = original
        render(current)
        for action in total_actions:
            current = current.apply(action)
            render(current)
            sleep(1)
        sleep(4)
