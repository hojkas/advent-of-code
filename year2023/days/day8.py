from typing import Optional
from enum import Enum

from lib.abstract_day import AbstractDay
from lib.exceptions import RunException
from helpers import InputLoader, regex_extract_multiple


class Direction(Enum):
    LEFT = 0
    RIGHT = 1


class Node:
    def __init__(self, node_string):
        self.name, self.left_path, self.right_path = regex_extract_multiple(r"(...) = \((...), (...)\)", node_string, 3)

    @property
    def is_start(self) -> bool:
        if self.name[2] == "A":
            return True
        return False

    @property
    def is_end(self) -> bool:
        if self.name[2] == "Z":
            return True
        return False


class Instructions:
    def __init__(self, instruction_string):
        self.items = []
        for item_string in instruction_string:
            if item_string == "R":
                self.items.append(Direction.RIGHT)
            elif item_string == "L":
                self.items.append(Direction.LEFT)
            else:
                raise RunException(f"Unknown instruction '{item_string}'")
        self.next_index = 0
        self.cycle_length = len(self.items)
        self.cycle = 0

    def next(self) -> Direction:
        item_to_return = self.items[self.next_index]
        if self.next_index + 1 == self.cycle_length:
            self.next_index = 0
            self.cycle += 1
        else:
            self.next_index += 1
        return item_to_return


class NodeMap:
    def __init__(self, input_string):
        instruction_string, node_strings = input_string.split("\n\n")
        self.instructions = Instructions(instruction_string)
        self.nodes = {}
        for node_string in node_strings.split("\n"):
            if node_string:
                node = Node(node_string)
                self.nodes[node.name] = node

    def go(self, from_node: str, direction: Direction) -> str:
        current_node = self.nodes[from_node]
        if direction == Direction.LEFT:
            return current_node.left_path
        else:
            return current_node.right_path


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_string = self.input_loader.load_input()
        node_map = NodeMap(input_string)
        result = part_one(node_map)
        return result

    def run_part_two(self):
        input_string = self.input_loader.load_input()
        node_map = NodeMap(input_string)
        result = part_two(node_map)
        return result


def part_one(node_map: NodeMap) -> int:
    current_node = "AAA"
    while True:
        next_instruction = node_map.instructions.next()
        current_node = node_map.go(current_node, next_instruction)
        if current_node == "ZZZ":
            break
    return node_map.instructions.cycle * node_map.instructions.cycle_length + node_map.instructions.next_index


def part_two(node_map: NodeMap) -> int:
    pass  # TODO
