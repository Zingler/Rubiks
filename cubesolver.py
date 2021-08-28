from structs import *
from astar import * 

class CubeProblem(Problem):
    def __init__(self, cube, actions=ACTIONS):
        self._initial_state = cube
        self._actions = actions
    def initial_state(self):
        return self._initial_state
    def goal_test(self, state):
        return state.solved()
    def actions(self, node):
        return filter_actions(self._actions, node.action)
    def apply_action(self, state, action):
        return state.apply(action), 1
    def heuristic(self, state):
        return state.turn_distance() / 4

if __name__ == "__main__":
    from plotter import start_plotter
    from time import sleep
    from random import randrange
    from astar import search

    render = start_plotter()

    cube = Cube(3)
    cube = cube.sub_cube(lambda b: True) 
    turns = 8

    for i in range(turns):
        cube = cube.apply(random.choice(ACTIONS))

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

