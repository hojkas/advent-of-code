from typing import Optional

from lib.abstract_day import AbstractDay
from helpers import InputLoader


class IdList:
    def __init__(self, id_list):
        self.id_list = sorted(id_list)
        self.id_list_generator = iter(self.id_list)
        self.number_map = {}
        for number in id_list:
            if number not in self.number_map:
                self.number_map[number] = 1
            else:
                self.number_map[number] += 1

    def next_smallest(self) -> int:
        """
        :raises StopIteration: when id_list is exhausted
        :return: next smallest id
        """
        return next(self.id_list_generator)


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_array = self.input_loader.load_input_array(item_separator="\n")
        first_id_list, second_id_list = assemble_id_lists(input_array)
        result = calculate_list_distance(first_id_list, second_id_list)
        return result

    def run_part_two(self):
        input_array = self.input_loader.load_input_array(item_separator="\n")
        first_id_list, second_id_list = assemble_id_lists(input_array)
        result = calculate_item_similarity_score(first_id_list, second_id_list)
        return result


def assemble_id_lists(input_array: list[str]) -> tuple[IdList, IdList]:
    first_list, second_list = [], []
    for line in input_array:
        first_item, second_item = (item for item in line.split(" ") if len(item) > 0)
        first_list.append(int(first_item))
        second_list.append(int(second_item))
    return IdList(first_list), IdList(second_list)


def calculate_list_distance(first_id_list: IdList, second_id_list: IdList) -> int:
    distance_sum = 0
    try:
        while True:
            first_item = first_id_list.next_smallest()
            second_item = second_id_list.next_smallest()
            distance_sum += abs(first_item - second_item)
    except StopIteration:
        pass

    return distance_sum


def calculate_item_similarity_score(first_id_list: IdList, second_id_list: IdList) -> int:
    similarity_score = 0
    for number, number_count in first_id_list.number_map.items():
        if number in second_id_list.number_map:
            similarity_score += number * number_count * second_id_list.number_map[number]
    return similarity_score
