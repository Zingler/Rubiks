from structs import *
from astar import * 


class CubeProblem(Problem):
    def __init__(self, cube):
        self._initial_state = cube
    def initial_state(self):
        return self._initial_state
    def goal_test(self, state):
        return state.solved()
    def actions(self, state):
        return ACTIONS
    def apply_action(self, state, action):
        return state.apply(action), 1
    def heuristic(self, state):
        return 0


if __name__ == "__main__":
    from plotter import render
    from time import sleep
    from random import randrange
    from astar import search

    cube = Cube(3)
    turns = 3

    for i in range(turns):
        cube = cube.apply(random.choice(ACTIONS))

    render(cube)

    p = CubeProblem(cube)
    states, actions = search(p)

    print(f'Solved in {len(actions)-1} turns')

    for i in range(20):
        current = cube
        render(current)
        for action in actions[1:]:
            current = current.apply(action)
            render(current)
        sleep(4)

