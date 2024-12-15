from dataclasses import dataclass

from lib.models.direction import Direction
from lib.exceptions import OutOfBoundsError


@dataclass
class MapVector:
    row_diff: int
    col_diff: int


@dataclass
class MapField:
    row: int
    col: int


@dataclass
class MapRepresentation:
    fields: list[list[MapField]]
    row_count: int
    col_count: int

    def __init__(self, fields: list[list[MapField]]):
        self.fields = fields
        self.row_count = len(fields)
        self.col_count = len(fields[0])

    def coordinates_within_bounds(self, row, col) -> bool:
        """
        Check if the coordinates are within the map bounds.
        :param row:
        :param col:
        :return: True if they are, false if not.
        """
        return 0 <= row < self.row_count and 0 <= col < self.col_count

    def get_next_field_in_direction(self, current_field: MapField, direction: Direction) -> MapField:
        """
        Fetch a field relative to current field in given direction.
        :param current_field:
        :param direction:
        :raise OutOfBoundsError: If the coordinates of the new field fall outside the map.
        :return: Fetched field.
        """
        vector_from_direction = MapVector(row_diff=direction.value[0], col_diff=direction.value[1])
        return self.get_next_field_by_offset(current_field, vector_from_direction)

    def get_next_field_by_offset(self, current_field: MapField, offset_vector: MapVector) -> MapField:
        """
        Fetch a field with row/col offset relative to current field.
        :param current_field:
        :param offset_vector:
        :raise OutOfBoundsError: If the coordinates of the new field fall outside the map.
        :return: Fetched field.
        """
        new_row = current_field.row + offset_vector.row_diff
        new_col = current_field.col + offset_vector.col_diff
        if not self.coordinates_within_bounds(new_row, new_col):
            raise OutOfBoundsError()
        return self.fields[new_row][new_col]
