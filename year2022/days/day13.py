from typing import Union
from enum import Enum

from abstract_day import AbstractDay
from helpers.input_loader import InputLoader


class PacketTuple:
    def __init__(self, input_string, index):
        split_string = input_string.strip().split("\n")
        if len(split_string) != 2:
            raise RuntimeError(f"Split of input went wrong: {str(split_string)}")
        self.first = eval(split_string[0])
        self.second = eval(split_string[1])
        self.index = index

    def __repr__(self):
        return f"1: {str(self.first)}\n2: {str(self.second)}"


class Status(Enum):
    CORRECT = 0
    INCORRECT = 1
    UNDECIDED = 2


def compare_lists(list1, list2):
    for item1, item2 in zip(list1, list2):
        item_status = compare_items(item1, item2)
        if item_status == Status.CORRECT or item_status == Status.INCORRECT:
            return item_status

    # one list run out of items
    if len(list1) < len(list2):
        return Status.CORRECT
    if len(list1) > len(list2):
        return Status.INCORRECT

    return Status.UNDECIDED


def compare_ints(int1, int2):
    if int1 < int2:
        return Status.CORRECT
    if int1 > int2:
        return Status.INCORRECT
    return Status.UNDECIDED


def compare_items(item1, item2):
    assert_item_type(item1)
    assert_item_type(item2)

    if type(item1) == int and type(item2) == int:
        return compare_ints(item1, item2)
    else:
        if type(item1) == int:
            item1 = [item1]
        if type(item2) == int:
            item2 = [item2]
        return compare_lists(item1, item2)


def assert_item_type(item):
    if type(item) not in [list, int]:
        raise RuntimeError(f"Unknown type of item (expected list or int): {type(item)}")


def load_packet_tuples(input_array):
    packet_tuples = []
    for i, input_part in enumerate(input_array):
        packet_tuples.append(PacketTuple(input_part, i+1))
    return packet_tuples


def load_singular_packets(input_array):
    packets = []
    for line in input_array:
        if len(line) != 0:
            packets.append(eval(line))
    return packets


def part_one(input_packet_list):
    correct_indices = 0
    for packet_tuple in input_packet_list:
        result = compare_lists(packet_tuple.first, packet_tuple.second)
        if result == Status.CORRECT:
            correct_indices += packet_tuple.index
        if result == Status.UNDECIDED:
            raise RuntimeError(f"At this point, the status should not be undecided. Packets: {packet_tuple}")
    return correct_indices


def how_many_packets_before(new_packet, packet_list):
    cnt = 0
    for packet in packet_list:
        comparison_status = compare_lists(packet, new_packet)
        if comparison_status == Status.CORRECT:
            cnt += 1
    return cnt


def part_two(packet_list):
    index_of_two = how_many_packets_before([[2]], packet_list) + 1
    index_of_six = how_many_packets_before([[6]], packet_list) + 2  # because it would be after two packet
    return index_of_two * index_of_six


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_packets = load_packet_tuples(self.input_loader.load_input_array("\n\n"))
        result = part_one(input_packets)
        return result

    def run_part_two(self):
        input_packets = load_singular_packets(self.input_loader.load_input_array("\n"))
        result = part_two(input_packets)
        return result
