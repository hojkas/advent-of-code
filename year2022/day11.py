import logging
import os
import re
from datetime import datetime
from typing import Union
from abstract_day import AbstractDay
from exceptions import RunException
from old_helpers import CC
from helpers.timethis import timethis
from input_loader import InputLoader

MAX_EFFECTIVE_WORRY_LEVEL = 2 * 3 * 5 * 7 * 11 * 13 * 17 * 19
next_item_id = 0


def regex_get(regex, string):
    match = re.search(regex, string)
    if match and len(match.groups()) > 0:
        return match.group(1)
    raise RunException("Regex '" + regex + "' failed to find match in '" + string + "'.")


def print_result(part, result):
    filename = os.path.basename(__file__).split('.')[0]
    print('[', filename, '] ', CC.GREEN, 'Result of part ', part, CC.NC, ': ', result, sep='')


class Monkey:
    def __init__(self, monkey_string, cooldown_after_inspection=True):
        monkey_lines = monkey_string.split("\n")
        self.id = int(regex_get(r"Monkey (\d+):", monkey_lines[0]))
        self.items = [Item(int(x)) for x in regex_get(r"Starting items: (.*?)$", monkey_lines[1]).split(", ")]
        self.operation = regex_get(r"Operation: new = (.*?)$", monkey_lines[2])
        self.test_divisible_by = int(regex_get(r"Test: divisible by (\d+)$", monkey_lines[3]))
        self.test_true_monkey = int(regex_get(r"If true: throw to monkey (\d+)$", monkey_lines[4]))
        self.test_false_monkey = int(regex_get(r"If false: throw to monkey (\d+)$", monkey_lines[5]))
        self.monkey_map = None
        self.inspections = 0
        self.turn_inspections_history = []
        self.this_turn_inspections = 0
        self.cooldown_after_inspection = cooldown_after_inspection

    def take_item(self, item):
        self.items.append(item)

    def add_monkey_map(self, monkey_map):
        self.monkey_map = monkey_map

    def print_inspection_history(self, last_n=None):
        inspection_history = self.turn_inspections_history
        if last_n:
            inspection_history = inspection_history[-last_n:]
        print(self.id, end=" | ")
        for history in inspection_history:
            print('{:3d}'.format(history), end=" ")
        print()

    def turn(self):
        self.this_turn_inspections = 0
        for item in self.items:
            self._proccess_item(item)
        self.items = []
        self.turn_inspections_history.append(self.this_turn_inspections)

    def _proccess_item(self, item):
        self.inspections += 1
        self.this_turn_inspections += 1
        self._inspect_item(item)
        self._cooldown_item(item)
        test_result = self._test_item(item)
        self._throw_to_monkey_based_on_test_result(item, test_result)

    def _inspect_item(self, item):
        old = item.worry_level
        item.set_worry_level(eval(self.operation))

    def _cooldown_item(self, item):
        if self.cooldown_after_inspection:
            item.set_worry_level(item.worry_level // 3)

    def _test_item(self, item):
        return item.worry_level % self.test_divisible_by == 0

    def _throw_to_monkey_based_on_test_result(self, item, test_result):
        if test_result:
            self.monkey_map[self.test_true_monkey].take_item(item)
        else:
            self.monkey_map[self.test_false_monkey].take_item(item)


class Item:
    def __init__(self, worry_level):
        global next_item_id
        self.worry_level = int(worry_level)
        self.id = next_item_id
        next_item_id += 1

    def set_worry_level(self, new_worry_level):
        if new_worry_level <= MAX_EFFECTIVE_WORRY_LEVEL:
            self.worry_level = new_worry_level
        else:
            self.worry_level = new_worry_level % MAX_EFFECTIVE_WORRY_LEVEL


def load_monkeys(input_array, cooldown_after_inspections=True):
    monkeys = []
    for monkey_string in input_array:
        monkeys.append(Monkey(monkey_string, cooldown_after_inspections))
    return monkeys


def create_monkey_map(monkey_list):
    monkey_map = {}
    for monkey in monkey_list:
        monkey_map[monkey.id] = monkey
    return monkey_map


def give_monkeys_monkey_map(monkey_list):
    monkey_map = create_monkey_map(monkey_list)
    for monkey in monkey_list:
        monkey.add_monkey_map(monkey_map)


def find_monkey_scheneningans(monkey_list):
    monkey_list.sort(key=lambda x: x.inspections)
    return monkey_list[-2].inspections * monkey_list[-1].inspections


def part_one(input_array):
    monkey_list = load_monkeys(input_array)
    give_monkeys_monkey_map(monkey_list)
    for i in range(20):
        for monkey in monkey_list:
            monkey.turn()
    return find_monkey_scheneningans(monkey_list)


def do_monkey_round(monkey_list):
    for monkey in monkey_list:
        monkey.turn()


def part_two(input_array):
    monkey_list = load_monkeys(input_array, False)
    give_monkeys_monkey_map(monkey_list)

    round_count = 0
    while True:
        round_count += 1
        do_monkey_round(monkey_list)
        if round_count == 10000:
            break

    return find_monkey_scheneningans(monkey_list)


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None
        self.debug_mode = False

    def dbg(self, *args, **kwargs):
        if self.debug_mode:
            print(*args, **kwargs)

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def use_debug(self, use_debug=False):
        self.debug_mode = use_debug

    def run_part_one(self):
        input_array = self.input_loader.load_input_array("\n\n")
        result = part_one(input_array)
        print_result(1, result)

    def run_part_two(self):
        input_array = self.input_loader.load_input_array("\n\n")
        result = part_two(input_array)
        print_result(2, result)
