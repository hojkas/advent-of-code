from typing import Optional, Generator
from enum import Enum

from lib.abstract_day import AbstractDay
from helpers import InputLoader


class CrosswordDirection(Enum):
    DOWN = 0
    UP = 1
    RIGHT = 2
    LEFT = 3
    DOWN_RIGHT = 4
    DOWN_LEFT = 5
    UP_RIGHT = 6
    UP_LEFT = 7


class ABox:
    def __init__(self, up_left: str, up_right: str, down_left: str, down_right: str):
        self.up_left = up_left
        self.up_right = up_right
        self.down_left = down_left
        self.down_right = down_right

    def is_xmas(self) -> bool:
        count = 0
        if self.up_left == "M":
            if self.down_right == "S":
                count += 1
        elif self.up_left == "S":
            if self.down_right == "M":
                count += 1

        if self.up_right == "M":
            if self.down_left == "S":
                count += 1
        elif self.up_right == "S":
            if self.down_left == "M":
                count += 1
        return count == 2


class CrosswordMap:
    def __init__(self, crossword_array: list[list[str]]):
        self.crossword_rows = crossword_array

    def slice_lines_across_direction(self, direction: CrosswordDirection) -> Generator[list[str], None, None]:
        # cardinal directions
        if direction == CrosswordDirection.DOWN:
            return self._slice_lines_vertical()
        if direction == CrosswordDirection.UP:
            return self._slice_lines_vertical(reverse=True)
        if direction == CrosswordDirection.RIGHT:
            return self._slice_lines_horizontal()
        if direction == CrosswordDirection.LEFT:
            return self._slice_lines_horizontal(reverse=True)
        # diagonals
        if direction == CrosswordDirection.DOWN_RIGHT:
            return self._slice_main_diagonal()
        if direction == CrosswordDirection.DOWN_LEFT:
            return self._slice_side_diagonal()
        if direction == CrosswordDirection.UP_LEFT:
            return self._slice_main_diagonal(reverse=True)
        if direction == CrosswordDirection.UP_RIGHT:
            return self._slice_side_diagonal(up_right=True)

    def _slice_lines_horizontal(self, reverse: bool = False) -> Generator[list[str], None, None]:
        if not reverse:
            return (line for line in self.crossword_rows)
        return (line[::-1] for line in self.crossword_rows)

    def _slice_lines_vertical(self, reverse: bool = False) -> Generator[list[str], None, None]:
        col = 0
        while col < len(self.crossword_rows[0]):
            if not reverse:
                yield [line[col] for line in self.crossword_rows]
            else:
                yield [line[col] for line in self.crossword_rows[::-1]]
            col += 1

    def _slice_main_diagonal(self, reverse: bool = False, allow_unsorted: bool = True) -> Generator[list[str], None, None]:
        if not allow_unsorted:
            raise NotImplementedError()

        def reverse_if_needed(item: list[str]) -> list[str]:
            if reverse:
                return item[::-1]
            return item

        row_length = len(self.crossword_rows[0])
        # main diagonal + under main diagonal
        for diagonal_offset_index in range(len(self.crossword_rows)):
            yield reverse_if_needed(
                [
                    row[i - diagonal_offset_index]
                    for i, row
                    in enumerate(self.crossword_rows)
                    if 0 <= i - diagonal_offset_index < row_length
                ]
            )

        # over main diagonal
        for diagonal_offset_index in range(1, len(self.crossword_rows[0])):
            yield reverse_if_needed(
                [
                    row[i + diagonal_offset_index]
                    for i, row
                    in enumerate(self.crossword_rows)
                    if 0 <= i + diagonal_offset_index < row_length
                ]
            )

    def _slice_side_diagonal(self, up_right: bool = False) -> Generator[list[str], None, None]:
        row_col_offset = 0
        row_length = len(self.crossword_rows[0])
        col_length = len(self.crossword_rows)
        max_row_col_offset = row_length + col_length - 2
        while row_col_offset <= max_row_col_offset:
            yield_item = [
                row[row_col_offset - row_index]
                for row_index, row
                in enumerate(self.crossword_rows)
                if 0 <= row_col_offset - row_index < row_length
            ]
            if not up_right:
                yield yield_item
            else:
                yield yield_item[::-1]
            row_col_offset += 1

    def gather_a_boxes(self) -> Generator[ABox, None, None]:
        row_count = len(self.crossword_rows)
        col_count = len(self.crossword_rows[0])

        for row_index, row in enumerate(self.crossword_rows):
            for col_index, char in enumerate(row):
                if char == "A" and 0 < row_index < row_count - 1 and 0 < col_index < col_count - 1:
                    yield ABox(
                        up_right=self.crossword_rows[row_index-1][col_index+1],
                        up_left=self.crossword_rows[row_index-1][col_index-1],
                        down_right=self.crossword_rows[row_index+1][col_index+1],
                        down_left=self.crossword_rows[row_index+1][col_index-1],
                    )


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_string_array = self.input_loader.load_input_array(item_separator="\n")
        crossword_map = CrosswordMap(input_string_array)
        result = count_crosswords(crossword_map)
        return result

    def run_part_two(self):
        input_string_array = self.input_loader.load_input_array(item_separator="\n")
        crossword_map = CrosswordMap(input_string_array)
        result = sum(1 for abox in crossword_map.gather_a_boxes() if abox.is_xmas())
        return result


def count_crosswords(crossword_map: CrosswordMap) -> int:
    matches = 0
    for direction in CrosswordDirection:
        for searchable_line in crossword_map.slice_lines_across_direction(direction):
            matches += count_matches_in_string_list(searchable_line)
    return matches


def count_matches_in_string_list(searchable_line: list[str]) -> int:
    matches = 0
    next_to_find = "X"
    for char in searchable_line:
        if char != next_to_find:
            next_to_find = "X"
            if char != "X":
                continue

        if next_to_find == "X":
            next_to_find = "M"
        elif next_to_find == "M":
            next_to_find = "A"
        elif next_to_find == "A":
            next_to_find = "S"
        elif next_to_find == "S":
            matches += 1
            next_to_find = "X"
        else:
            raise RuntimeError(f"Unexpected character in searchline: {next_to_find}")

    return matches
