from dataclasses import dataclass

from lib.models.direction import Direction
from lib.exceptions import OutOfBoundsError


@dataclass
class MapVector:
    row_diff: int
    col_diff: int


@dataclass
class GenericMapField:
    row: int
    col: int


@dataclass
class GenericMapRepresentation:
    fields: list[list[GenericMapField]]

    def __init__(self, fields: list[list[GenericMapField]]):
        self.fields = fields

    @property
    def row_count(self):
        return len(self.fields)

    @property
    def col_count(self):
        return len(self.fields[0])

    def coordinates_within_bounds(self, row, col) -> bool:
        """
        Check if the coordinates are within the map bounds.
        :param row:
        :param col:
        :return: True if they are, false if not.
        """
        return 0 <= row < self.row_count and 0 <= col < self.col_count

    def get_cardinal_neighbouring_fields(
        self, current_field: GenericMapField, include_empty: bool = True
    ) -> dict[Direction, GenericMapField]:
        """
        Get all neighbouring fields in cardinal directions of current field.
        :param current_field:
        :param include_empty: If true, fields out of bounds will return as None under direction key. If false, the direction
        itself will be left out of keys.
        :return: Dictionary where keys are directions and values the fields.
        """
        neighbours = {}
        for direction in Direction.get_cardinal():
            try:
                field = self.get_next_field_in_direction(current_field, direction)
                neighbours[direction] = field
            except OutOfBoundsError:
                if include_empty:
                    neighbours[direction] = None
        return neighbours

    def get_next_field_in_direction(self, current_field: GenericMapField, direction: Direction) -> GenericMapField:
        """
        Fetch a field relative to current field in given direction.
        :param current_field:
        :param direction:
        :raise OutOfBoundsError: If the coordinates of the new field fall outside the map.
        :return: Fetched field.
        """
        vector_from_direction = MapVector(row_diff=direction.value[0], col_diff=direction.value[1])
        return self.get_next_field_by_offset(current_field, vector_from_direction)

    def get_next_field_by_offset(self, current_field: GenericMapField, offset_vector: MapVector) -> GenericMapField:
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
