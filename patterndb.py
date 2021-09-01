from permutation import permutations
from orientationcalc import calc_edge_orientations
from structs import ACTIONS, HALF_FACE, HALF_Z, QUARTER_X, QUARTER_Y, Cube, center, corner, edge, filter_actions, top
import pickle


def vector_id(x, y, z):
    return chr((x+1)*9+(y+1)*3+(z+1)+97)


def orientation_id(os):
    one = one_hot_cold_encoding(*os[0])
    two = one_hot_cold_encoding(*os[1])
    return chr(one*6+two+97)


encoding = [
    [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
    [[2, 2, 2], [4, None, 5], [3, 3, 3]],
    [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
]


def one_hot_cold_encoding(x, y, z):
    return encoding[x+1][y+1][z+1]


def position_from_id(id_string):
    id = ord(id_string) - 97
    z = id % 3 - 1
    id //= 3
    y = id % 3 - 1
    id //= 3
    x = id % 3 - 1
    return [x, y, z]


class KeyGenerator:
    def key(self, blocks):
        return "".join(self.block_key(b) for b in blocks)

    def block_key(self, block):
        pass


class ActualLocationKeyGenerator(KeyGenerator):
    def block_key(self, block):
        return vector_id(*block.actual_location)


class OrientationKeyGenerator(KeyGenerator):
    def block_key(self, block):
        return orientation_id(block.orientations)

class CornerOrientationAxisKeyGenerator(KeyGenerator):
    def key(self, blocks):
        result = ''
        for i in range(0, len(blocks), 5):
            num = 0
            for b in blocks[i:i+5]:
                num *= 3
                num += [abs(m) for m in b.orientations[0]].index(1)
            result += chr(num+97)
        return result

class EdgeOrientationKeyGen:
    def __init__(self) -> None:
        self.valid_orientations = calc_edge_orientations(QUARTER_X+QUARTER_Y+HALF_Z)

    def key(self, blocks):
        result = ''
        for i in range(0, len(blocks), 5):
            num = 0
            for b in blocks[i:i+5]:
                num <<= 1
                num += tuple(b.orientations) in self.valid_orientations[b.solved_location]
            result += chr(num+97)
        return result


class EdgeSliceKeyGen:
    def slice_num(self, b):
        slice_array = [m == 0 for m in b.solved_location]
        return slice_array.index(True)

    def key(self, blocks):
        result = ''
        for i in range(0, len(blocks), 5):
            num = 0
            for b in blocks[i:i+5]:
                num *= 3
                num += self.slice_num(b)
            result += chr(num+97)
        return result


class PatternDBData:
    pass


class PatternDB:
    def __init__(self, ordered_positions=[],
                 default_value=0,
                 match_on_solved_location=True,
                 key_generators=[ActualLocationKeyGenerator, OrientationKeyGenerator],
                 data=None):
        if data:
            self.data = data
        else:
            self.data = PatternDBData()
            self.data.ordered_positions = ordered_positions
            self.data.db = {}
            self.data.default_value = default_value
            self.data.matching_on_solved_location = match_on_solved_location
            self.data.key_generator_classes = key_generators

        if self.data.matching_on_solved_location:
            self.matcher = lambda p: lambda b: b.solved_location == p
        else:
            self.matcher = lambda p: lambda b: b.actual_location == p
        self.key_generators = [c() for c in self.data.key_generator_classes]

    def create_key(self, blocks):
        if not self.data.matching_on_solved_location:  # Reorder blocks based on actual location
            blocks = self.matching_blocks(blocks)
        array = [gen.key(blocks) for gen in self.key_generators]
        return ''.join(array)

    def insert_if_not_present(self, blocks, value):
        key = self.create_key(blocks)
        if key not in self.data.db:
            self.data.db[key] = value
            return True
        return False

    def insert_full_cube(self, cube: Cube, value):
        return self.insert_if_not_present(cube.blocks, value)

    def insert_cube_with_permutations(self, cube: Cube, value):
        blocks = cube.blocks
        inserted_anything = False
        for p in permutations(blocks):
            inserted_anything |= self.insert_if_not_present(p, value)
        return inserted_anything

    def matching_blocks(self, blocks):
        def find(l, lamb):
            for x in l:
                if lamb(x):
                    return x
            return None
        result = []
        for p in self.data.ordered_positions:
            block = find(blocks, self.matcher(p))
            result.append(block)
        return result

    def matching_blocks_from_cube(self, cube: Cube):
        return self.matching_blocks(cube.blocks)

    def get_from_cube(self, cube: Cube):
        blocks = self.matching_blocks_from_cube(cube)
        return self.get(blocks)

    def get(self, blocks):
        key = self.create_key(blocks)
        if key in self.data.db:
            return self.data.db[key]
        else:
            return self.data.default_value

    def contains_cube(self, cube):
        blocks = self.matching_blocks_from_cube(cube)
        return self.create_key(blocks) in self.data.db


def corner_perm_db():
    cube = Cube(3).sub_cube(corner)
    return build_db("corner_perm", cube, 10, actions=HALF_FACE, pattern_db_options={
        "key_generators": [ActualLocationKeyGenerator]
    })


def build_db(name, cube: Cube, max_depth, actions=ACTIONS, insert_all_permutations=False, pattern_db_options={}):
    cube = cube.sub_cube(~center)
    filepath = f"dbs/{name}.db"
    try:
        db_data = pickle.load(open(filepath, "rb"))
        return PatternDB(data=db_data)
    except:
        pass

    db = PatternDB(ordered_positions=[b.solved_location for b in cube.blocks], default_value=max_depth+1, **pattern_db_options)

    def recurse(cube, depth, remaining_actions, previous_action):
        nonlocal actions
        if remaining_actions == 0:
            if insert_all_permutations:
                return db.insert_cube_with_permutations(cube, depth)
            else:
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
            print("Halting before max depth as all states have be found already")
            break
    print(f"[{name}]: Built db with {len(db.data.db)} elements. Saving to disk.")
    pickle.dump(db.data, open(filepath, "wb"))
    return db


if __name__ == "__main__":
    from structs import Vector
    cube = Cube(3)
    cube = cube.sub_cube(top & edge)

    built_db = build_db("test", cube, 4)
    print("db size", len(built_db.data.db))

    edge_cube = Cube(3).sub_cube(edge)
    build_db("edgetest", edge_cube, 6, pattern_db_options={
        "match_on_solved_location": False,
        "key_generators": [EdgeOrientationKeyGen]
    })
