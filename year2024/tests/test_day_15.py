import pytest

from lib.models import Direction
from year2024.days.day15 import Robot, FactoryMap, FactoryMapField, FieldType, InstructionSet, parse_factory_map


TEST_MOVE_SETUP_1 = """
############
##........##
##.....[].##
##[][][]..##
##...[][].##
##....[][]##
##....@...##
############
"""
TEST_MOVE_INSTRUCTIONS_1 = [Direction.UP]
TEST_MOVE_EXPECTED_RESULT_1 = """
############
##.....[].##
##..[][]..##
##[].[][].##
##....[]..##
##....@.[]##
##........##
############
"""

TEST_MOVE_SETUP_2 = """
#################
##......[][].@.##
#################
"""
TEST_MOVE_INSTRUCTIONS_2 = [
    Direction.UP, Direction.LEFT, Direction.LEFT, Direction.LEFT, Direction.DOWN, Direction.RIGHT
]
TEST_MOVE_EXPECTED_RESULT_2 = """
#################
##....[][].@...##
#################
"""

TEST_INVALID_MOVE_SETUP_1 = """
############
##......[]##
##.....[].##
##[][][]..##
##...[][].##
##....[][]##
##....@...##
############
"""
TEST_INVALID_MOVE_INSTRUCTIONS_1 = [Direction.UP]
TEST_INVALID_MOVE_EXPECTED_RESULT_1 = """
############
##......[]##
##.....[].##
##[][][]..##
##...[][].##
##....[][]##
##....@...##
############
"""


@pytest.mark.parametrize(
    "setup, instructions, expected_result",
    [
        (TEST_INVALID_MOVE_SETUP_1, TEST_INVALID_MOVE_INSTRUCTIONS_1, TEST_INVALID_MOVE_EXPECTED_RESULT_1),
        (TEST_MOVE_SETUP_1, TEST_MOVE_INSTRUCTIONS_1, TEST_MOVE_EXPECTED_RESULT_1),
        (TEST_MOVE_SETUP_2, TEST_MOVE_INSTRUCTIONS_2, TEST_MOVE_EXPECTED_RESULT_2),
    ]
)
def test_move_robot(setup: str, instructions: list[Direction], expected_result: str):
    robot_map = load_setup(setup.strip(), instructions)
    while robot_map.process_next_instruction(wide_version=True):
        pass
    assert check_expected_result(robot_map, expected_result.strip())


def load_setup(raw_setup: str, instructions: list[Direction]) -> FactoryMap:
    return parse_factory_map(raw_setup, InstructionSet(instructions))


def check_expected_result(robot_map: FactoryMap, expected_result: str) -> bool:
    differences = []
    for row_id, row in enumerate(expected_result.splitlines()):
        for col_id, char in enumerate(row):
            real_value = (
                "@"
                if robot_map.robot.row == row_id and robot_map.robot.col == col_id
                else robot_map.fields[row_id][col_id].type.value
            )
            if char != real_value:
                differences.append((row_id, col_id, char, real_value))

    if differences:
        print("\nRobot map:")
        robot_map.print_map()
        print(f"Expected:\n{expected_result}")
        print("Differences:")
        for diff in differences:
            print(f"[{diff[0]}, {diff[1]}] expected {diff[2]}, got {diff[3]}")
        return False

    return True
