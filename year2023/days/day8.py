from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import math

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

    def go_node(self, from_node: Node, direction: Direction) -> Node:
        if direction == Direction.LEFT:
            return self.nodes[from_node.left_path]
        else:
            return self.nodes[from_node.right_path]


@dataclass
class GhostNodeEnd:
    ending_node: Node
    sequence_index: int


@dataclass
class GhostNodePath:
    starting_node: Node
    end_nodes: list[GhostNodeEnd] = field(default_factory=list)
    pattern_start_index: Optional[int] = None
    pattern_length: Optional[int] = None
    end_nodes_pattern_indices: list[int] = field(default_factory=list)

    def get_end_at_index(self, index) -> Optional[GhostNodeEnd]:
        for ghost_end in self.end_nodes:
            if ghost_end.sequence_index == index:
                return ghost_end
        return None


@dataclass
class SimplifiedPath:
    starting_index: int
    pattern_length: int
    end_indices: list[int]


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
    ghost_node_paths = [GhostNodePath(node_name) for node_name in node_map.nodes.values() if node_name.is_start]
    for ghost_node_path in ghost_node_paths:
        calculate_path_until_repeat(ghost_node_path, node_map)
    simple_paths = load_into_simple_paths(ghost_node_paths)
    # unoptimized because the puzzle obviously expects the pattern to be noticed and not found like this
    # first_index_all_ends = find_first_time_when_all_are_ends(simple_paths)
    first_index_all_ends = find_common_index(simple_paths)
    return first_index_all_ends


def load_into_simple_paths(ghost_node_paths: list[GhostNodePath]) -> list[SimplifiedPath]:
    return [
        SimplifiedPath(
            ghost_node_path.pattern_start_index,
            ghost_node_path.pattern_length,
            ghost_node_path.end_nodes_pattern_indices
        )
        for ghost_node_path in ghost_node_paths
    ]


def calculate_path_until_repeat(ghost_node_path: GhostNodePath, node_map: NodeMap) -> None:
    node_index = 0
    current_node = ghost_node_path.starting_node

    while True:
        next_instruction = node_map.instructions.next()
        current_node = node_map.go_node(current_node, next_instruction)
        node_index += 1

        if current_node.is_end:
            ghost_node_path.end_nodes.append(GhostNodeEnd(current_node, node_index))

        if len([end for end in ghost_node_path.end_nodes if end.ending_node == current_node]) > 1:
            # at least two nodes with the name already found
            result = find_pattern(ghost_node_path)
            if result:
                fill_node_end_indices(ghost_node_path)
                break


def find_pattern(ghost_node_path: GhostNodePath) -> bool:
    ends_in_reverse = ghost_node_path.end_nodes[::-1]
    anchor_end_node = ends_in_reverse[0].ending_node
    anchor_locations = [end.sequence_index for end in ends_in_reverse if end.ending_node == anchor_end_node]

    for secondary_anchor_index in anchor_locations[1:]:
        length = 0
        primary_index = anchor_locations[0]
        secondary_index = secondary_anchor_index

        while True:
            primary_index -= 1
            secondary_index -= 1
            length += 1

            if secondary_index < 0:
                break

            if primary_index == secondary_anchor_index:
                ghost_node_path.pattern_length = length
                ghost_node_path.pattern_start_index = secondary_index + 1
                return True

            primary_position_node = ghost_node_path.get_end_at_index(primary_index)
            secondary_position_node = ghost_node_path.get_end_at_index(secondary_index)

            if primary_position_node is None and secondary_position_node is None:
                continue
            elif (
                    primary_position_node is not None and
                    secondary_position_node is not None and
                    primary_position_node.ending_node == secondary_position_node.ending_node
            ):
                continue

            break

    return False


def fill_node_end_indices(ghost_node_path: GhostNodePath) -> None:
    first_relevant_index = ghost_node_path.pattern_start_index
    last_relevant_index = first_relevant_index + ghost_node_path.pattern_length - 1

    for node_end in ghost_node_path.end_nodes:
        if first_relevant_index <= node_end.sequence_index <= last_relevant_index:
            ghost_node_path.end_nodes_pattern_indices.append(node_end.sequence_index - first_relevant_index)


def find_common_index(simple_paths: list[SimplifiedPath]) -> int:
    return math.lcm(*[path.pattern_length for path in simple_paths])


# the following part would work but is unoptimized for the large number it is
# it tried to find the number by not assuming there is only one end in each pattern
# thus being much more complicated task, left here for completeness sake
@dataclass
class IncrementingEnd:
    index: int
    increment: int


@dataclass
class OrConditionedIncrementingEnds:
    ends: list[IncrementingEnd] = field(default_factory=list)

    def get_smallest(self) -> int:
        smallest = None
        for end in self.ends:
            if smallest is None or end.index < smallest:
                smallest = end.index
        return smallest

    def increment_smallest(self) -> None:
        smallest = None
        for end in self.ends:
            if smallest is None or end.index < smallest.index:
                smallest = end
        smallest.index += smallest.increment


@dataclass
class IncrementingEndOrGroups:
    end_groups: list[OrConditionedIncrementingEnds] = field(default_factory=list)

    def increment_smallest(self) -> None:
        group_smallest = {}
        for group in self.end_groups:
            group_smallest[group.get_smallest()] = group
        smallest_item = sorted(list(group_smallest.keys()))[0]
        group_smallest[smallest_item].increment_smallest()

    def all_groups_contain_same_end(self) -> Optional[int]:
        ends = {}
        for group in self.end_groups:
            for end in group.ends:
                if end.index not in ends:
                    ends[end.index] = 1
                else:
                    ends[end.index] += 1

        for end_value, end_count in ends.items():
            if len(self.end_groups) == end_count:
                return end_value

        return None


def find_first_time_when_all_are_ends(simple_paths: list[SimplifiedPath]) -> int:
    inc_end_groups = IncrementingEndOrGroups()
    for simple_path in simple_paths:
        or_end_group = OrConditionedIncrementingEnds()
        for end_index in simple_path.end_indices:
            or_end_group.ends.append(
                IncrementingEnd(simple_path.starting_index + end_index, simple_path.pattern_length)
            )
        inc_end_groups.end_groups.append(or_end_group)

    while True:
        same_end_index = inc_end_groups.all_groups_contain_same_end()
        if same_end_index is not None:
            return same_end_index

        inc_end_groups.increment_smallest()
