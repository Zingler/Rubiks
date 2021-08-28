from structs import ACTIONS, QUARTER_X, Cube, edge, filter_actions, top
import pickle

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

class PatternDBData:
    pass


class PatternDB:
    def __init__(self, ordered_positions=[], default_value=0, match_on_solved_location=True, data=None):
        if data:
            self.data = data
        else:
            self.data = PatternDBData()
            self.data.ordered_positions = ordered_positions
            self.data.db = {}
            self.data.default_value = default_value
            self.data.matching_on_solved_location = match_on_solved_location

        if self.data.matching_on_solved_location:
            self.matcher = lambda p: lambda b: b.solved_location == p
        else:
            self.matcher = lambda p: lambda b: b.actual_location == p
    
    def create_key(self, blocks):
        array = [vector_id(*b.actual_location) for b in blocks] + [vector_id(*o) for b in blocks for o in b.orientations]
        return ''.join(array)
    
    def insert_if_not_present(self, blocks, value):
        key = self.create_key(blocks)
        if key not in self.data.db:
            self.data.db[key] = value
            return True
        return False
    
    def insert_full_cube(self, cube:Cube, value):
        return self.insert_if_not_present(cube.blocks, value)
    
    def matching_blocks_from_cube(self, cube:Cube):
        def find(l, lamb):
            for x in l:
                if lamb(x):
                    return x
            return None

        blocks = cube.blocks
        result = []
        for p in self.data.ordered_positions:
            block = find(blocks, self.matcher(p))
            result.append(block)
        return result
    
    def get_from_cube(self, cube:Cube):
        blocks = self.matching_blocks_from_cube(cube)
        return self.get(blocks)

    def get(self, blocks):
        key = self.create_key(blocks)
        if key in self.data.db:
            return self.data.db[key]
        else:
            return self.data.default_value

def build_db(name, cube:Cube, max_depth, actions=ACTIONS):
    filepath = f"dbs/{name}.db"
    try:
        db_data = pickle.load(open(filepath, "rb"))
        return PatternDB(data=db_data)
    except:
        pass
    
    db = PatternDB(ordered_positions=[b.solved_location for b in cube.blocks], default_value=max_depth+1)

    def recurse(cube, depth, remaining_actions, previous_action):
        nonlocal actions
        if remaining_actions == 0:
            return db.insert_full_cube(cube, depth)
        inserted_something = False
        for a in filter_actions(actions, previous_action):
            did_insert = recurse(cube.apply(a), depth, remaining_actions-1, a)
            inserted_something |= did_insert
        return inserted_something
    
    for d in range(max_depth):
        print(f"[{name}]: Building DB level {d}")
        inserted_something = recurse(cube, d, d, None)
        if not inserted_something:
            print("Halting before max depth as all states had be found already")
            break;
    print(f"[{name}]: Built db with {len(db.data.db)} elements. Saving to disk.")
    pickle.dump(db.data, open(filepath, "wb"))
    return db

if __name__ == "__main__":
    from structs import Vector
    cube = Cube(3)
    cube = cube.sub_cube(top & edge)

    built_db = build_db("test", cube, 4)
    print("db size", len(built_db.data.db))

