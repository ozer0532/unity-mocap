from dataclasses import dataclass


@dataclass
class Point(object):
    x: float
    y: float

    def __str__(self) -> str:
        return "[%.4f %.4f]" % (self.x, self.y)

    def __repr__(self) -> str:
        return self.__str__()

    def __iter__(self):
        yield self.x
        yield self.y


@dataclass
class Point3D(object):
    x: float
    y: float
    z: float

    def __str__(self) -> str:
        return "[%.4f %.4f %.4f]" % (self.x, self.y, self.z)

    def __repr__(self) -> str:
        return self.__str__()

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z
