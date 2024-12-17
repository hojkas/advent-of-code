from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from helpers import InputLoader
from lib.abstract_day import AbstractDay


class StoneRule(Enum):
    MAKE_ONE = 0
    SPLIT = 1
    MULTIPLY = 2


@dataclass
class StoneState:
    value: int
    count: int = 1

    def applicable_rule(self) -> StoneRule:
        if self.value == 0:
            return StoneRule.MAKE_ONE
        if len(str(self.value)) % 2 == 0:
            return StoneRule.SPLIT
        return StoneRule.MULTIPLY


@dataclass
class BasicStoneLine:
    stones: dict[int, StoneState] = field(default_factory=dict)

    def execute_blink(self) -> None:
        stones = list(self.stones.values())
        self.stones = {}
        for stone in stones:
            stone_rule = stone.applicable_rule()
            self.apply_rule_to_stone_and_save(stone, stone_rule)

    def apply_rule_to_stone_and_save(self, stone: StoneState, rule: StoneRule) -> None:
        if rule == StoneRule.MAKE_ONE:
            self.add_stone(StoneState(value=1, count=stone.count))
            return

        if rule == StoneRule.MULTIPLY:
            self.add_stone(StoneState(value=stone.value*2024, count=stone.count))
            return

        # StoneRule.SPLIT
        value_as_string = str(stone.value)
        firstpart, secondpart = value_as_string[:len(value_as_string) // 2], value_as_string[len(value_as_string) // 2:]
        first_new_stone = StoneState(value=int(firstpart), count=stone.count)
        second_new_stone = StoneState(value=int(secondpart), count=stone.count)
        self.add_stone(first_new_stone)
        self.add_stone(second_new_stone)

    def add_stone(self, stone: StoneState) -> None:
        if stone.value in self.stones:
            self.stones[stone.value].count += stone.count
        else:
            self.stones[stone.value] = stone

    def count_stones(self) -> int:
        return sum(stone.count for stone in self.stones.values())


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        stone_line = parse_basic_stone_line(self.input_loader.load_input_array(" "))
        for x in range(25):
            stone_line.execute_blink()
        return stone_line.count_stones()

    def run_part_two(self):
        stone_line = parse_basic_stone_line(self.input_loader.load_input_array(" "))
        for x in range(75):
            stone_line.execute_blink()
        return stone_line.count_stones()


def parse_basic_stone_line(raw_stones: list[str]) -> BasicStoneLine:
    stone_line = BasicStoneLine()
    for raw_stone in raw_stones:
        stone_value = int(raw_stone)
        stone = StoneState(stone_value)
        stone_line.add_stone(stone)
    return stone_line


# 4048 should be there, instead, i have 4048
