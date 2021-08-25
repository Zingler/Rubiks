from dataclasses import InitVar, dataclass
from typing import OrderedDict


@dataclass(eq=True, frozen=True)
class Vector:
    x: int
    y: int
    z: int
    
    def rotateX(self):
        return Vector(self.x, self.z, -self.y)
    def rotateY(self):
        return Vector(self.z, self.y, -self.x)
    def rotateZ(self):
        return Vector(-self.y, self.x, self.z)
    def halfX(self):
        return Vector(self.x, -self.y, -self.z)
    def halfY(self):
        return Vector(-self.x, self.y, -self.z)
    def halfZ(self):
        return Vector(-self.x, -self.y, self.z)

    def rrotateX(self):
        return Vector(self.x, -self.z, self.y)
    def rrotateY(self):
        return Vector(-self.z, self.y, self.x)
    def rrotateZ(self):
        return Vector(self.y, -self.x, self.z)

    def cross(self, o):
        return Vector(self.y*o.z - o.y*self.z, o.x*self.z - self.x*o.z, self.x*o.y - self.y*o.x)
    
    def copy(self):
        return Vector(self.x, self.y, self.z)
    def __add__(one, two):
        return Vector(one.x+two.x, one.y+two.y, one.z+two.z)
    def __mul__(self, scalar):
        return Vector(self.x*scalar, self.y*scalar, self.z*scalar)
    def __eq__(self, o):
        return self.x == o.x and self.y == o.y and self.z == o.z
    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __str__(self) -> str:
        return f'[{self.x}, {self.y}, {self.z}]'
    def __repr__(self) -> str:
        return self.__str__()


class Matrix:
    def __init__(self, c1,c2,c3):
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3

    def __mul__(self, v):
        x = self.c1.x*v.x + self.c2.x*v.y + self.c3.x*v.z
        y = self.c1.y*v.x + self.c2.y*v.y + self.c3.y*v.z
        z = self.c1.z*v.x + self.c2.z*v.y + self.c3.z*v.z
        return Vector(x,y,z)
    
    @staticmethod
    def rotor(v1,v2):
        return Matrix(v1,v2,v1.cross(v2))

class Block:
    initial_orientations = [Vector(1,0,0), Vector(0,1,0)]

    def __init__(self, solved_location, actual_location=None, orientations=None):
        self.solved_location = solved_location
        self.actual_location = actual_location or solved_location.copy()
        self.orientations = orientations or Block.initial_orientations
        self._hash = None
    
    def apply(self, action):
        if action.applies(self):
            actual_location = action.transform.__call__(self.actual_location)
            orientations = [action.transform.__call__(o) for o in self.orientations]
            return Block(self.solved_location, actual_location, orientations)
        else:
            return self
    
    def solved(self):
        return self.solved_location == self.actual_location and (self.orientations == Block.initial_orientations or self.is_center())
    
    def is_corner(self):
        l = self.solved_location
        return l.x != 0 and l.y != 0 and l.z != 0

    def is_center(self):
        l = self.solved_location
        return (l.x == 0) + (l.y == 0) + (l.z == 0) == 2

    def turn_distance(self):
        right_location = self.solved_location == self.actual_location 
        right_o = (self.orientations == Block.initial_orientations)
        if right_location and right_o:
            return 0
        if right_location and not right_o:
            return 3
        if self.is_corner():
           return (self.solved_location.x != self.actual_location.x) + (self.solved_location.y != self.actual_location.y) + (self.solved_location.z != self.actual_location.z)
        return 1

    def __str__(self) -> str:
        return f'(L=[{self.actual_location.x}, {self.actual_location.y}, {self.actual_location.z}], O=[{self.orientation.x}, {self.orientation.y}, {self.orientation.z}])'
    def __repr__(self) -> str:
        return self.__str__()
    def __eq__(self, other):
        return self.actual_location == other.actual_location and self.orientations == other.orientations # and self.solved_location == other.solved_location 
    def __hash__(self): 
        if not self._hash:
            self._hash = hash((self.solved_location, self.actual_location, self.orientations[0], self.orientations[1]))
        return self._hash

class Cube:
    def __init__(self, size, blocks=None):
        self.size = size
        if blocks == None:
            self.blocks = []
            even = size % 2 == 0
            half = int(size / 2)
            for i in range(-half, half+1):
                for j in range(-half, half+1):
                    for k in range(-half, half+1):
                        interior = all([abs(x) != half for x in (i,j,k)])
                        if not (even and i*j*k == 0) and not interior:
                            self.blocks.append(Block(Vector(i,j,k)))
        else:
            self.blocks = blocks
        self._hash = None

    def apply(self, action):
       blocks = [b.apply(action) for b in self.blocks] 
       return Cube(self.size, blocks=blocks)
    
    def sub_cube(self, block_selector):
        blocks = []
        for b in self.blocks:
            if block_selector(b):
                blocks.append(b)
        return Cube(self.size, blocks)

    
    def solved(self):
        return all((b.solved() for b in self.blocks))

    def turn_distance(self):
        return sum((b.turn_distance() for b in self.blocks)) 
    
    def __eq__(self, other):
        return self.blocks == other.blocks
    def __hash__(self): 
        # return super().__hash__()
        if not self._hash:
            self._hash = hash(tuple([hash(b) for b in self.blocks]))
        return self._hash


class Action:
    _id_generator = 0

    def __init__(self, applies, transform, inverse=None):
        self.applies = applies
        self.transform = transform
        if isinstance(inverse, Action):
            self.inverse = inverse
        elif inverse is None:
            self.inverse = self
        else:
            self.inverse = Action(applies, inverse, self)
    
    def id(self):
        if not hasattr(self,'_id'):
            Action._id_generator += 1
            self._id = Action._id_generator
        return self._id
    
    def __hash__(self) -> int:
        return self.id()

    def __eq__(self, other) -> bool:
        return self.id() == other.id()


QUARTER_FACE = [
    Action(lambda b: b.actual_location.x == 1, Vector.rotateX, Vector.rrotateX),
    Action(lambda b: b.actual_location.x == -1, Vector.rotateX, Vector.rrotateX),
    Action(lambda b: b.actual_location.y == 1, Vector.rotateY, Vector.rrotateY),
    Action(lambda b: b.actual_location.y == -1, Vector.rotateY, Vector.rrotateY),
    Action(lambda b: b.actual_location.z == 1, Vector.rotateZ, Vector.rrotateZ),
    Action(lambda b: b.actual_location.z == -1, Vector.rotateZ, Vector.rrotateZ),
]

HALF_FACE = [
    Action(lambda b: b.actual_location.x == 1, Vector.halfX),
    Action(lambda b: b.actual_location.x == -1, Vector.halfX),
    Action(lambda b: b.actual_location.y == 1, Vector.halfY),
    Action(lambda b: b.actual_location.y == -1, Vector.halfY),
    Action(lambda b: b.actual_location.z == 1, Vector.halfZ),
    Action(lambda b: b.actual_location.z == -1, Vector.halfZ)
]

ACTIONS = QUARTER_FACE + list(map(lambda a: a.inverse, QUARTER_FACE)) + HALF_FACE


if __name__ == "__main__":
    # Performance testing

    import random
    import timeit

    iterations = 40_000
    cube = Cube(3)

    start = timeit.default_timer()

    for i in range(iterations):
        ai = random.randrange(len(ACTIONS))
        cube = cube.apply(ACTIONS[ai])
    
    end = timeit.default_timer()
    print(f'Actions per second {iterations/(end-start)}')