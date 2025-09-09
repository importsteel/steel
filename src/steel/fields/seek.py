from typing import Callable, Iterable

import steel

type Seeker = Callable[[int], int]


class Test(steel.Structure):
    a = steel.Integer(size=4)
    b = steel.Integer(size=4)
    c = steel.Integer(size=4)
    d = steel.Integer(size=4)


def offset(absolute: int) -> Seeker:
    return lambda position: absolute


def advance(distance: int) -> Seeker:
    return lambda position: position + distance


def rewind(distance: int) -> Seeker:
    return lambda position: position - distance


def deferred(lookup_func: Callable[[], Seeker]) -> Seeker:
    return lambda position: lookup_func()(position)


def variable_advance(distance: int) -> Seeker:
    return deferred(lambda: lambda position: position + distance)


def lookup(steps: Iterable[Seeker]) -> int:
    position = 0
    for step in steps:
        print(position)
        position = step(position)
    print(position)
    return position


steps = [
    advance(4),  # Integer(size=4)
    advance(4),  # Integer(size=4)
    advance(2),  # Integer(size=2)
    variable_advance(10),  # TerminatedString()
    offset(0x100),
]


if __name__ == "__main__":
    lookup(steps)

# class Seeker:
#     __slots__ = ["position"]
#     position: int

#     def offset(self, position: int) -> int:
#         """
#         Seek to absolute position {position}
#         """
#         self.position = position
#         return self.position

#     def advance(self, distance: int) -> int:
#         """
#         Seek to absolute position {position}
#         """
#         self.position += distance
#         return self.position

#     def rewind(self, distance: int) -> int:
#         self.position -= distance
#         return self.position

#     def advance_lazy(self, evaluator: function) -> int:
#         seeker_func = evaluator()
#         return seeker_func(self)
