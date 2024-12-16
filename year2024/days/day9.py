from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from lib.abstract_day import AbstractDay
from helpers import InputLoader


class BlockType(Enum):
    EMPTY = 0
    DATA = 1


@dataclass
class BasicBlock:
    type: BlockType
    id: Optional[int] = None


@dataclass
class BasicDisc:
    blocks: list[BasicBlock] = field(default_factory=list)
    unsorted_empty_blocks: list[tuple[int, BasicBlock]] = field(default_factory=list)
    unsorted_data_blocks: list[tuple[int, BasicBlock]] = field(default_factory=list)

    def _setup_unsorted_blocks(self):
        self.unsorted_empty_blocks = []
        self.unsorted_data_blocks = []

        for i, block in enumerate(self.blocks):
            if block.type == BlockType.EMPTY:
                self.unsorted_empty_blocks.append((i, block))
            else:
                self.unsorted_data_blocks.append((i, block))

    def _find_last_data_block(self) -> tuple[int, BasicBlock]:
        if len(self.unsorted_data_blocks) == 0:
            return 0, self.blocks[0]
        return self.unsorted_data_blocks.pop(-1)

    def _find_first_empty_block(self) -> tuple[int, BasicBlock]:
        if len(self.unsorted_empty_blocks) == 0:
            return len(self.blocks), self.blocks[-1]
        return self.unsorted_empty_blocks.pop(0)

    def calculate_checksum(self) -> int:
        checksum = 0
        for index, block in enumerate(self.blocks):
            if block.type == BlockType.DATA:
                checksum += index * block.id
        return checksum

    def do_simple_defragmentation(self) -> None:
        self._setup_unsorted_blocks()
        while self._do_single_simple_defragmentation_step():
            pass

    def _do_single_simple_defragmentation_step(self) -> bool:
        data_block_index, data_block = self._find_last_data_block()
        empty_block_index, empty_block = self._find_first_empty_block()
        if empty_block_index > data_block_index:
            return False

        self.blocks[data_block_index] = empty_block
        self.blocks[empty_block_index] = data_block
        return True


@dataclass
class AdvancedBlock:
    start_index: int
    length: int
    type: BlockType


@dataclass
class DataBlock(AdvancedBlock):
    id: Optional[int] = None
    type: BlockType = BlockType.DATA


@dataclass
class EmptyBlock(AdvancedBlock):
    type: BlockType = BlockType.EMPTY
    prev_empty_block: Optional['EmptyBlock'] = None
    next_empty_block: Optional['EmptyBlock'] = None

    def can_be_split(self, length: int) -> bool:
        return self.length >= length

    def split(self, new_length: int) -> Optional['EmptyBlock']:
        if not self.can_be_split(new_length):
            raise ValueError(f"Cannot split block with length {self.length} into {new_length}")

        if self.length == new_length:
            return None  # do no split, the whole block will be filled

        new_block = EmptyBlock(start_index=self.start_index + new_length, length=self.length - new_length)
        self.length = new_length
        new_block.next_empty_block = self.next_empty_block
        new_block.prev_empty_block = self
        self.next_empty_block.prev_empty_block = new_block
        self.next_empty_block = new_block
        return new_block

    def rebind_neighbours_to_each_other(self) -> None:
        if self.prev_empty_block:
            self.prev_empty_block.next_empty_block = self.next_empty_block
        if self.next_empty_block:
            self.next_empty_block.prev_empty_block = self.prev_empty_block

    def cancel_bindings(self) -> None:
        self.prev_empty_block = None
        self.next_empty_block = None


@dataclass
class AdvancedDisc:
    blocks: list[AdvancedBlock] = field(default_factory=list)
    first_empty_block: Optional['EmptyBlock'] = None
    unmoved_data_blocks: list[AdvancedBlock] = field(default_factory=list)

    def calculate_checksum(self) -> int:
        checksum = 0
        for block in self.blocks:
            if isinstance(block, DataBlock):
                index = block.start_index
                for _ in range(block.length):
                    checksum += index * block.id
                    index += 1
        return checksum

    def defragment(self) -> None:
        while len(self.unmoved_data_blocks) > 0:
            self._do_one_defragment_step()

    def _do_one_defragment_step(self) -> None:
        data_to_move = self.unmoved_data_blocks.pop(-1)
        empty_space_for_data = None
        current_empty_space_to_check = self.first_empty_block
        while True:
            if current_empty_space_to_check.start_index > data_to_move.start_index:
                break  # data would be moved back, not forward, abort
            if current_empty_space_to_check.can_be_split(data_to_move.length):
                empty_space_for_data = current_empty_space_to_check
                break
            current_empty_space_to_check = current_empty_space_to_check.next_empty_block
            if current_empty_space_to_check is None:
                break

        if empty_space_for_data is None:
            return  # data cannot be moved anywhere

        leftover_empty_space = empty_space_for_data.split(data_to_move.length)
        if leftover_empty_space:
            self.blocks.append(leftover_empty_space)

        if empty_space_for_data.prev_empty_block is None:
            self.first_empty_block = empty_space_for_data.next_empty_block  # if first, bind second to the position

        empty_space_for_data.rebind_neighbours_to_each_other()
        empty_space_for_data.cancel_bindings()
        data_to_move.start_index, empty_space_for_data.start_index = empty_space_for_data.start_index, data_to_move.start_index


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_line = self.input_loader.load_input().strip()
        disc = parse_input_disc_data(input_line)
        disc.do_simple_defragmentation()
        return disc.calculate_checksum()  # should be 2858

    def run_part_two(self):
        input_line = self.input_loader.load_input().strip()
        advanced_disc = parse_input_into_advanced_disc_data(input_line)
        advanced_disc.defragment()
        return advanced_disc.calculate_checksum()


def parse_input_disc_data(input_line: str) -> BasicDisc:
    disc = BasicDisc()
    next_is_data_block = True
    next_data_block_id = 0

    for char in input_line:
        block_length = int(char)
        if next_is_data_block:
            for _ in range(block_length):
                disc.blocks.append(BasicBlock(type=BlockType.DATA, id=next_data_block_id))
            next_is_data_block = False
            next_data_block_id += 1
        else:
            for _ in range(block_length):
                disc.blocks.append(BasicBlock(type=BlockType.EMPTY))
            next_is_data_block = True

    return disc


def parse_input_into_advanced_disc_data(input_line: str) -> AdvancedDisc:
    disc = AdvancedDisc()
    next_is_data_block = True
    next_data_block_id = 0
    data_index = 0
    previous_empty_block = None

    for char in input_line:
        block_length = int(char)
        if next_is_data_block:
            if block_length > 0:
                block = DataBlock(start_index=data_index, length=block_length, id=next_data_block_id)
                disc.blocks.append(block)
                disc.unmoved_data_blocks.append(block)
            next_data_block_id += 1
            next_is_data_block = False
        else:
            if block_length > 0:
                block = EmptyBlock(start_index=data_index, length=block_length)
                disc.blocks.append(block)
                if previous_empty_block is None:
                    disc.first_empty_block = block
                else:
                    previous_empty_block.next_empty_block = block
                block.prev_empty_block = previous_empty_block
                previous_empty_block = block
            next_is_data_block = True

        data_index += block_length

    return disc
