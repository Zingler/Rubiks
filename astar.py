from collections import defaultdict
from typing import Any
from indexqueue import IndexedQueue
from queue import PriorityQueue
from dataclasses import dataclass
import math
import random

@dataclass
class Node:
    state: Any
    path_cost: float
    parent: Any
    action: Any
    
    def __hash__(self) -> int:
        return hash(self.state)

    def __eq__(self, o: object) -> bool:
        return self.state == o.state
    
    def __str__(self):
        return f"{self.state}, path_cost={self.path_cost}"
    
class Problem:
    def initial_state(self):
        pass
    def goal_test(self, state):
        return False
    def actions(self, node):
        return []
    def child(self, node, action) -> Node:
        state, path_cost = self.apply_action(node.state, action)
        return Node(state, node.path_cost + path_cost, node, action)
    def apply_action(self, state, action):
        return (None, None)
    def cost(self, node):
        return node.path_cost + self.heuristic(node.state)
    def heuristic(self, state):
        return 0


def search(problem, callback=None, callback_freq=1_000):
    node = Node(problem.initial_state(), 0, None, None)
    frontier = IndexedQueue()
    frontier.add_or_update(0, node)
    explored = set()
    action_count = 0

    final_node = None
    iteration = 0
    while not frontier.empty():
        iteration += 1
        (priority, node) = frontier.pop()

        if (callback and iteration % callback_freq == 0):
            callback({
                "cost": priority,
                "uniform_cost": node.path_cost,
                "state": node.state,
                "explored_nodes": len(explored),
                "action_count": action_count
            })

        if problem.goal_test(node.state):
            final_node = node
            break
        explored.add(node)

        for action in problem.actions(node):
            child = problem.child(node, action)
            action_count += 1
            if not child in explored:
                existing_node = frontier.get(child)
                child_cost = problem.cost(child)
                if not existing_node or existing_node[0] > child_cost:
                    frontier.add_or_update(child_cost, child)
    if final_node:
        states = []
        actions = []
        current = final_node
        while current:
            states.append(current.state)
            actions.append(current.action)
            current = current.parent

        states.reverse()
        actions.reverse()
        print(f"Explored nodes = {len(explored)}")
        print(f"Actions taken = {action_count}")
        return states, actions
    else:
        return None, None

def iddfs(problem, callback=None, callback_freq=1_000):
    original_node = Node(problem.initial_state(), 0, None, None)
    state_count = 0

    def recurse(node, remaining_actions):
        nonlocal state_count
        if remaining_actions == 0:
            state_count = state_count + 1
            if callback and state_count % callback_freq == 0:
                callback({ "state": node.state})

            if problem.goal_test(node.state):
                return True, []
            else:
                return False, []
        
        new_actions = problem.actions(node)
        for a in new_actions:
            child = problem.child(node, a)
            solved, actions = recurse(child, remaining_actions-1)
            if solved:
                return True, [a] + actions
        return False, []

    max_depth = 0
    while True:
        print("Working on depth "+str(max_depth))
        solved, actions = recurse(original_node, max_depth)
        if solved:
            print("Solved at depth "+str(max_depth))
            return [], [None]+actions # Implement returning states later if needed. Just here to match astar return format.
        max_depth+=1

if __name__ == "__main__":
    # Example of finding shortest path with heuristic of straight line distance
    @dataclass(eq=True, frozen=True)
    class Location:
        x: int
        y: int

        def dist(self, location):
            return math.sqrt((self.x - location.x)**2 + (self.y - location.y)**2)

    class ShortestPath(Problem):
        def __init__(self, num_locations):
            self.locations = []
            self.locations.append(Location(0,0))
            for i in range(num_locations-2):
                l = Location(random.randint(0,100), random.randint(0,100))
                self.locations.append(l)
            self.locations.append(Location(100,100))
            self.paths = defaultdict(set)
            current = self.locations[0]
            path_count = int(num_locations * num_locations // 2 * .3)
            i = 0
            while i < path_count:
                new = random.choice(self.locations)
                if i == path_count - 1:
                    new = self.locations[-1]
                if not current == new and (current.dist(new) < 50 or i == path_count -1):
                    self.paths[current].add(new)
                    self.paths[new].add(current)
                    i = i + 1
                    current = new
        def initial_state(self):
            return self.locations[0]
        def goal_test(self, state):
            return state == self.locations[-1]
        def actions(self, state):
            return self.paths[state]
        def apply_action(self, state, action) -> Node:
            return action, state.dist(action)
        def heuristic(self, state):
            return state.dist(self.locations[-1])

    problem = ShortestPath(40)
    states, actions = search(problem)

    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib import collections  as mc

    fig, ax = plt.subplots()

    lines = []
    for start, ends in problem.paths.items():
        for e in ends:
            lines.append([(start.x, start.y), (e.x, e.y)])
    
    lc = mc.LineCollection(lines, colors="grey")
    ax.add_collection(lc)

    solution = []
    for i in range(len(states)-1):
        s = states[i]
        e = states[i+1]
        solution.append([(s.x,s.y), (e.x,e.y)])

    lc = mc.LineCollection(solution, colors="blue")
    ax.add_collection(lc)

    plt.scatter([l.x for l in problem.locations], [l.y for l in problem.locations])
    plt.show()


