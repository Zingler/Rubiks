from structs import ACTIONS, QUARTER_X, Cube

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
    def __init__(self, solved_positions):
        self.solved_positions = solved_positions
        self.db = {}
    
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
            return None

def build_db(cube:Cube, max_depth, actions=ACTIONS):
    db = PatternDB([b.solved_location for b in cube.blocks])

    def recurse(cube, depth, remaining_actions):
        nonlocal actions
        if remaining_actions == 0:
            db.insert_full_cube(cube, depth)
            return
        for a in actions: # TODO:Performance: filter inverse actions
            recurse(cube.apply(a), depth, remaining_actions-1)
    
    for d in range(max_depth):
        print(f"Building DB level {d}")
        recurse(cube, d, d)
    return db

if __name__ == "__main__":
    from structs import Vector


    cube = Cube(3)
    cube = cube.sub_cube(lambda b: b.solved_location.x == 1 and b.solved_location.y == 1 and abs(b.solved_location.z) == 1)
    db = PatternDB([b.solved_location for b in cube.blocks])

    db.insert_full_cube(cube, 3)
    cube = cube.apply(QUARTER_X[0])
    db.insert_full_cube(cube, 4)
    print(db.db)
    print(db.get_from_cube(cube))


    built_db = build_db(cube, 5)
    print("Built db size", len(built_db.db))

