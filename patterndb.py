from structs import ACTIONS, QUARTER_X, Cube, edge, filter_actions, top

def vector_id(x,y,z):
    return chr((x+1)*9+(y+1)*3+(z+1)+97)

def position_from_id(id_string):
    id = ord(id_string) - 97
    z = id%3 - 1
    id //= 3
    y = id%3 - 1
    id //= 3
    x = id%3 - 1
    return [x,y,z]

class PatternDB:
    def __init__(self, solved_positions, default):
        self.solved_positions = solved_positions
        self.db = {}
        self.default = default
    
    def create_key(self, blocks):
        array = [vector_id(*b.actual_location) for b in blocks] + [vector_id(*o) for b in blocks for o in b.orientations]
        return ''.join(array)
    
    def insert_if_not_present(self, blocks, value):
        key = self.create_key(blocks)
        if key not in self.db:
            self.db[key] = value
    
    def insert_full_cube(self, cube:Cube, value):
        self.insert_if_not_present(cube.blocks, value)
    
    def matching_blocks_from_cube(self, cube:Cube):
        def find(l, lamb):
            for x in l:
                if lamb(x):
                    return x
            return None

        blocks = cube.blocks
        result = []
        for p in self.solved_positions:
            block = find(blocks, lambda x: x.solved_location == p)
            result.append(block)
        return result
    
    def get_from_cube(self, cube:Cube):
        blocks = self.matching_blocks_from_cube(cube)
        return self.get(blocks)

    def get(self, blocks):
        key = self.create_key(blocks)
        if key in self.db:
            return self.db[key]
        else:
            return self.default

def build_db(cube:Cube, max_depth, actions=ACTIONS):
    db = PatternDB([b.solved_location for b in cube.blocks], default=max_depth+1)

    def recurse(cube, depth, remaining_actions, previous_action):
        nonlocal actions
        if remaining_actions == 0:
            db.insert_full_cube(cube, depth)
            return
        for a in filter_actions(actions, previous_action):
            recurse(cube.apply(a), depth, remaining_actions-1, a)
    
    for d in range(max_depth):
        print(f"Building DB level {d}")
        recurse(cube, d, d, None)
    print(f"Built db with {len(db.db)} elements")
    return db

if __name__ == "__main__":
    from structs import Vector


    cube = Cube(3)
    cube = cube.sub_cube(top & edge)
    print(cube.blocks)
    db = PatternDB([b.solved_location for b in cube.blocks])

    built_db = build_db(cube, 6)
    print("Built db size", len(built_db.db))

