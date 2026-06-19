from enum import Enum


class BarricadeType(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class Barricade:

    def __init__(self, row: int, col: int, barricade_type: BarricadeType):

        self.row = row
        self.col = col
        self.type = barricade_type

    @property
    def cells(self):

        if self.type == BarricadeType.HORIZONTAL:

            return [
                (self.row, self.col),
                (self.row, self.col + 2),
            ]

        return [
            (self.row, self.col),
            (self.row + 2, self.col),
        ]

    def intersections(self):
        if self.type == BarricadeType.HORIZONTAL:

            return [
                (self.row, self.col + 1)
            ]

        return [
            (self.row + 1, self.col)
        ]
    def __repr__(self):

        return (
            f"Barricade({self.row}, "
            f"{self.col}, "
            f"{self.type.name})"
        )