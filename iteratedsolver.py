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

    original = Cube(3)
    turns = 20

    for i in range(turns):
        original = original.apply(random.choice(ACTIONS))

    i = 1
    total_actions = []

    def sorter(block):
        l = block.solved_location
        return (l.z != 1, block.is_corner())
    blocks = sorted(original.blocks, key=sorter)
    running = Cube(3, blocks)
    
    while i < 8:
        cube = Cube(3, running.blocks[0:i])
        print(f"solving peice {i}")
    
        render(cube)
    
        def callback(status):
            print(status)
            render(status["state"])    
            pass
    
        p = CubeProblem(cube)
        states, actions = search(p, callback=callback, callback_freq=100)

        print(f'Solved in {len(actions)-1} turns')

        total_actions.extend(actions[1:])

        for a in actions[1:]:
            running = running.apply(a)
            
        render(running)
        sleep(1)

        i+=1

    print(f"Solved in {len(total_actions)} turns")

    for i in range(20):
        current = original
        render(current)
        for action in total_actions:
            current = current.apply(action)
            render(current)
            sleep(1)
        sleep(4)

