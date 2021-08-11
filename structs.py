class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def rotateX(self):
        return Vector(self.x, self.z, -self.y)
    def rotateY(self):
        return Vector(self.z, self.y, -self.x)
    def rotateZ(self):
        return Vector(-self.y, self.x, self.z)

    def cross(self, o):
        return Vector(self.y*o.z - o.y*self.z, o.x*self.z - self.x*o.z, self.x*o.y - self.y*o.x)
    
    def copy(self):
        return Vector(self.x, self.y, self.z)
    def __add__(one, two):
        return Vector(one.x+two.x, one.y+two.y, one.z+two.z)
    def __mul__(self, scalar):
        return Vector(self.x*scalar, self.y*scalar, self.z*scalar)

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
    def __init__(self, solved_location, actual_location=None, orientations=None):
        self.solved_location = solved_location
        self.actual_location = actual_location or solved_location.copy()
        self.orientations = orientations or [Vector(0,0,1), Vector(1,0,0)]
    
    def apply(self, action):
        if action.applies(self):
            actual_location = action.transform.__call__(self.actual_location)
            orientations = [action.transform.__call__(o) for o in self.orientations]
            return Block(self.solved_location, actual_location, orientations)
        else:
            return self

    def __str__(self) -> str:
        return f'(L=[{self.actual_location.x}, {self.actual_location.y}, {self.actual_location.z}], O=[{self.orientation.x}, {self.orientation.y}, {self.orientation.z}])'
    def __repr__(self) -> str:
        return self.__str__()

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

    def apply(self, action):
       blocks = [b.apply(action) for b in self.blocks] 
       return Cube(self.size, blocks=blocks)


class Action:
    def __init__(self, applies, transform):
        self.applies = applies
        self.transform = transform

ACTIONS = [
    Action(lambda b: b.actual_location.x == 1, Vector.rotateX),
    Action(lambda b: b.actual_location.x == -1, Vector.rotateX),
    Action(lambda b: b.actual_location.y == 1, Vector.rotateY),
    Action(lambda b: b.actual_location.y == -1, Vector.rotateY),
    Action(lambda b: b.actual_location.z == 1, Vector.rotateZ),
    Action(lambda b: b.actual_location.z == -1, Vector.rotateZ),
]


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