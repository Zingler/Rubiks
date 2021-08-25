from structs import *
from astar import * 


class CubeProblem(Problem):
    def __init__(self, cube):
        self._initial_state = cube
    def initial_state(self):
        return self._initial_state
    def goal_test(self, state):
        return state.solved()
    def actions(self, node):
        copy = ACTIONS[:]
        action = node.action
        if action:
            copy.remove(node.action.inverse)
        return copy
    def apply_action(self, state, action):
        return state.apply(action), 1
    def heuristic(self, state):
        return state.turn_distance() / 8


if __name__ == "__main__":
    from plotter import start_plotter
    from time import sleep
    from random import randrange
    from astar import search

    render = start_plotter()

    cube = Cube(3)
    def top(block: Block):
        l = block.solved_location
        x = l.x
        y = l.y
        z = l.z
        return z == 1
    def edge(block: Block):
        l = block.solved_location
        x = l.x
        y = l.y
        z = l.z
        return (x == 0) ^ (y == 0) ^ (z == 0)
    def corner(block: Block):
        l = block.solved_location
        x = l.x
        y = l.y
        z = l.z
        return (x != 0) and (y != 0) and (z != 0)
    def center(block: Block):
        l = block.solved_location
        x = l.x
        y = l.y
        z = l.z
        return ((x == 0) + (y == 0) + (z == 0)) == 2
    cube = cube.sub_cube(lambda b: True) 
    turns = 30

    for i in range(turns):
        cube = cube.apply(random.choice(ACTIONS))

    render(cube)

    def callback(status):
        print(status)
        render(status["state"])    

    # import cProfile
    # with cProfile.Profile() as pr:
    p = CubeProblem(cube)
    states, actions = search(p, callback=callback, callback_freq=10)
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

