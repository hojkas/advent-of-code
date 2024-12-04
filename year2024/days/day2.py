from typing import Optional
from enum import Enum

from lib.abstract_day import AbstractDay
from helpers import InputLoader


class Report:
    def __init__(self, report_list: list[int]):
        self.levels: list[int] = report_list

    def is_all_decreasing_safely(self, can_ignore_one_level: bool = False) -> bool:
        return self._levels_are_changing_within_limits(
            next_item_min_diff=-3, next_item_max_diff=-1, can_ignore_one_level=can_ignore_one_level
        )

    def is_all_increasing_safely(self, can_ignore_one_level: bool = False) -> bool:
        return self._levels_are_changing_within_limits(
            next_item_min_diff=1, next_item_max_diff=3, can_ignore_one_level=can_ignore_one_level
        )

    def _levels_are_changing_within_limits(
            self, next_item_min_diff: int, next_item_max_diff: int, can_ignore_one_level: bool = False
    ) -> bool:
        last_item = None
        levels_are_safe_without_delete = list_is_changing_within_limits(self.levels, next_item_min_diff, next_item_max_diff)

        if not can_ignore_one_level:
            return levels_are_safe_without_delete

        # at this point, list is faulty but maybe can be fixed
        level_variations = self._prepare_level_variations()
        return any(
            list_is_changing_within_limits(level_variations, next_item_min_diff, next_item_max_diff)
            for level_variations
            in level_variations
        )

    def _prepare_level_variations(self) -> list[list[int]]:
        level_variations = []
        for i in range(len(self.levels)):
            new_level_variation = self.levels.copy()
            new_level_variation.pop(i)
            level_variations.append(new_level_variation)
        return level_variations


def list_is_changing_within_limits(
    number_list: list[int], next_item_min_diff: int, next_item_max_diff: int
) -> bool:
    last_item = None
    for current_item in number_list:
        if not level_change_safe(
            current_item=current_item,
            last_item=last_item,
            next_item_min_diff=next_item_min_diff,
            next_item_max_diff=next_item_max_diff,
        ):
            return False
        last_item = current_item
    return True


def level_change_safe(
    current_item: int,
    last_item: Optional[int],
    next_item_min_diff: int,
    next_item_max_diff: int,
) -> bool:
    if last_item is None:
        return True
    last_item_diff = current_item - last_item
    return next_item_min_diff <= last_item_diff <= next_item_max_diff


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_lists = self.input_loader.load_input_array_of_array(
            subarray_separator="\n", item_separator=" ", retype_item_to_int=True
        )
        reports = [Report(input_list) for input_list in input_lists]
        return len([1 for r in reports if r.is_all_decreasing_safely() or r.is_all_increasing_safely()])

    def run_part_two(self):
        input_lists = self.input_loader.load_input_array_of_array(
            subarray_separator="\n", item_separator=" ", retype_item_to_int=True
        )
        reports = [Report(input_list) for input_list in input_lists]
        return len([
            1
            for r in reports
            if r.is_all_decreasing_safely(can_ignore_one_level=True) or r.is_all_increasing_safely(can_ignore_one_level=True)
        ])
