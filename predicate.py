class Predicate:
    def __init__(self, function):
        self.function = function
    def __call__(self, *args, **kwds):
        return self.function(*args, **kwds)
    def __or__(self, other):
        return Predicate(lambda *args, **kwds: self(*args, **kwds) or other(*args, **kwds))
    def __and__(self, other):
        return Predicate(lambda *args, **kwds: self(*args, **kwds) and other(*args, **kwds))

