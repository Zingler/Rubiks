from patterndb import build_db
from structs import *
from astar import * 

class CubeProblem(Problem):
    def __init__(self, cube, actions=ACTIONS):
        self._initial_state = cube
        self._actions = actions

        model_cube = Cube(3).sub_cube(top)
        edge_cube = model_cube.sub_cube(edge)
        corner_cube = model_cube.sub_cube(corner)
        pair_cube = model_cube.sub_cube(lambda b: b.solved_location.x == 1 and b.solved_location.y != -1)
        self._dbs = [build_db("korfedge", edge_cube, 6, ACTIONS),
                     build_db("korfcorner", corner_cube, 6, ACTIONS),
                     build_db("korffull", model_cube, 6, ACTIONS),
                     build_db("korfpair", pair_cube, 7, ACTIONS)]
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
        return max(state.turn_distance() / 8, db_lookup)

if __name__ == "__main__":
    from plotter import start_plotter
    from time import sleep
    from random import randrange
    from astar import search

    render = start_plotter()

    cube = Cube(3)
    cube = cube.sub_cube(top) 
    turns = 12

    previous = None
    for i in range(turns):
        action = random.choice(filter_actions(ACTIONS, previous)) # More likely to give a good shuffle rather than pure random
        cube = cube.apply(action)
        previous = action

    render(cube)

    def callback(status):
        print(status)
        render(status["state"])    

    # import cProfile
    # with cProfile.Profile() as pr:
    p = CubeProblem(cube)
    states, actions = search(p, callback=callback, callback_freq=100)
    # pr.print_stats()


    print(f'Solved in {len(actions)-1} turns')

    for i in range(20):
        current = cube
        render(current)
        for action in actions[1:]:
            current = current.apply(action)
            render(current)
            sleep(1)
        sleep(4)

