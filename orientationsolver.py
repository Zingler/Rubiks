from structs import *
from astar import * 
from orientationcalc import *

valid_edge_orientations = calc_edge_orientations(QUARTER_X + QUARTER_Y + HALF_Z)



class OrientationProblem(Problem):
    def __init__(self, cube, actions):
        self._initial_state = cube
        self._actions = actions
    def initial_state(self):
        return self._initial_state
    def goal_test(self, state):
        count = self.wrong_orientation_count(state)
        return count == 0
    def actions(self, node):
        copy = self._actions[:]
        action = node.action
        if action:
            copy.remove(node.action.inverse)
        return copy
    def apply_action(self, state, action):
        return state.apply(action), 1
    def heuristic(self, state):
        return self.wrong_orientation_count(state) / 4

    def wrong_orientation_count(self, state):
        sum = 0
        for b in state.blocks:
            o = tuple(b.orientations)
            if o not in valid_edge_orientations:
                sum += 1
        return sum


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
    cube = cube.sub_cube(lambda b: edge(b)) 
    turns = 30

    for i in range(turns):
        cube = cube.apply(random.choice(ACTIONS))

    render(cube)

    def callback(status):
        print(status)
        render(status["state"])    

    # import cProfile
    # with cProfile.Profile() as pr:
    p = OrientationProblem(cube, ACTIONS)
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

