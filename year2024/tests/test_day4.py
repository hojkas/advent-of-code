import pytest

from year2024.days.day4 import CrosswordDirection, CrosswordMap


TEST_CROSSWORD_BASIC = [
    ["1A", "1B", "1C", "1D"],
    ["2A", "2B", "2C", "2D"],
    ["3A", "3B", "3C", "3D"],
]

BASIC_EXPECTED_DOWN = [
    ["1A", "2A", "3A"],
    ["1B", "2B", "3B"],
    ["1C", "2C", "3C"],
    ["1D", "2D", "3D"],
]
BASIC_EXPECTED_UP = [result_row[::-1] for result_row in BASIC_EXPECTED_DOWN]
BASIC_EXPECTED_RIGHT = TEST_CROSSWORD_BASIC
BASIC_EXPECTED_LEFT = [result_row[::-1] for result_row in BASIC_EXPECTED_RIGHT]
BASIC_EXPECTED_DOWN_RIGHT = [
    ["3A"],
    ["2A", "3B"],
    ["1A", "2B", "3C"],
    ["1B", "2C", "3D"],
    ["1C", "2D"],
    ["1D"],
]
BASIC_EXPECTED_UP_LEFT = [result_row[::-1] for result_row in BASIC_EXPECTED_DOWN_RIGHT]
BASIC_EXPECTED_DOWN_LEFT = [
    ["1A"],
    ["1B", "2A"],
    ["1C", "2B", "3A"],
    ["1D", "2C", "3B"],
    ["2D", "3C"],
    ["3D"],
]
BASIC_EXPECTED_UP_RIGHT = [result_row[::-1] for result_row in BASIC_EXPECTED_DOWN_LEFT]
BASIC_EXPECTED_RESULTS = {
    CrosswordDirection.DOWN: BASIC_EXPECTED_DOWN,
    CrosswordDirection.UP: BASIC_EXPECTED_UP,
    CrosswordDirection.RIGHT: BASIC_EXPECTED_RIGHT,
    CrosswordDirection.LEFT: BASIC_EXPECTED_LEFT,
    CrosswordDirection.DOWN_RIGHT: BASIC_EXPECTED_DOWN_RIGHT,
    CrosswordDirection.UP_RIGHT: BASIC_EXPECTED_UP_RIGHT,
    CrosswordDirection.DOWN_LEFT: BASIC_EXPECTED_DOWN_LEFT,
    CrosswordDirection.UP_LEFT: BASIC_EXPECTED_UP_LEFT,
}


TEST_CROSSWORD_DIAGONAL_1 = [
    ["1", "2", "3", "4", "5"],
]
DIAGONAL_1_EXPECTED_RESULTS = {
    CrosswordDirection.DOWN_LEFT: [["1"], ["2"], ["3"], ["4"], ["5"]],
    CrosswordDirection.DOWN_RIGHT:  [["1"], ["2"], ["3"], ["4"], ["5"]],
    CrosswordDirection.UP_RIGHT: [["1"], ["2"], ["3"], ["4"], ["5"]],
    CrosswordDirection.UP_LEFT: [["1"], ["2"], ["3"], ["4"], ["5"]],
}

TEST_CROSSWORD_DIAGONAL_2 = [
    ["1A", "1B"],
    ["2A", "2B"],
    ["3A", "3B"],
    ["4A", "4B"],
]
DIAGONAL_2_EXPECTED_DOWN_RIGHT = [
    ["1B"],
    ["1A", "2B"],
    ["2A", "3B"],
    ["3A", "4B"],
    ["4A"],
]
DIAGONAL_2_EXPECTED_DOWN_LEFT = [
    ["1A"],
    ["1B", "2A"],
    ["2B", "3A"],
    ["3B", "4A"],
    ["4B"],
]
DIAGONAL_2_EXPECTED_RESULTS = {
    CrosswordDirection.DOWN_LEFT: DIAGONAL_2_EXPECTED_DOWN_LEFT,
    CrosswordDirection.DOWN_RIGHT: DIAGONAL_2_EXPECTED_DOWN_RIGHT,
    CrosswordDirection.UP_RIGHT: [result_row[::-1] for result_row in DIAGONAL_2_EXPECTED_DOWN_LEFT],
    CrosswordDirection.UP_LEFT: [result_row[::-1] for result_row in DIAGONAL_2_EXPECTED_DOWN_RIGHT],
}


def test_basic_crossword_direction_slice():
    crossword_map = CrosswordMap(TEST_CROSSWORD_BASIC)
    for direction in [CrosswordDirection.UP, CrosswordDirection.DOWN, CrosswordDirection.RIGHT, CrosswordDirection.LEFT]:
        expected_result = BASIC_EXPECTED_RESULTS[direction]
        _test_crossword_direction_slice(crossword_map, direction, expected_result)


@pytest.mark.parametrize(
    "crossword_map_strings, expected_results",
    [
        (TEST_CROSSWORD_BASIC, BASIC_EXPECTED_RESULTS),
        (TEST_CROSSWORD_DIAGONAL_1, DIAGONAL_1_EXPECTED_RESULTS),
        (TEST_CROSSWORD_DIAGONAL_2, DIAGONAL_2_EXPECTED_RESULTS),
    ]
)
def test_crossword_diagonal_direction_slice(
    crossword_map_strings: list[list[str]], expected_results: dict[CrosswordDirection, list[list[str]]]
):
    crossword_map = CrosswordMap(crossword_map_strings)
    for direction in [
        CrosswordDirection.DOWN_LEFT, CrosswordDirection.UP_LEFT, CrosswordDirection.DOWN_RIGHT, CrosswordDirection.UP_RIGHT
    ]:
        expected_result = expected_results[direction]
        _test_crossword_direction_slice(crossword_map, direction, expected_result)


def _test_crossword_direction_slice(crossword_map: CrosswordMap, direction: CrosswordDirection, expected_result: list[list[str]]):
    sliced_lines = list(crossword_map.slice_lines_across_direction(direction))
    assert len(sliced_lines) == len(expected_result)
    for line in sliced_lines:
        assert line in expected_result
