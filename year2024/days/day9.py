from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from lib.abstract_day import AbstractDay
from helpers import InputLoader


class BlockType(Enum):
    EMPTY = 0
    DATA = 1


@dataclass
class Block:
    type: BlockType
    id: Optional[int] = None


@dataclass
class Disc:
    blocks: list[Block] = field(default_factory=list)
    unsorted_empty_blocks: list[tuple[int, Block]] = field(default_factory=list)
    unsorted_data_blocks: list[tuple[int, Block]] = field(default_factory=list)

    def _setup_unsorted_blocks(self):
        self.unsorted_empty_blocks = []
        self.unsorted_data_blocks = []

        for i, block in enumerate(self.blocks):
            if block.type == BlockType.EMPTY:
                self.unsorted_empty_blocks.append((i, block))
            else:
                self.unsorted_data_blocks.append((i, block))

    def _find_last_data_block(self) -> tuple[int, Block]:
        if len(self.unsorted_data_blocks) == 0:
            return 0, self.blocks[0]
        return self.unsorted_data_blocks.pop(-1)

    def _find_first_empty_block(self) -> tuple[int, Block]:
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


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_line = self.input_loader.load_input().strip()
        disc = parse_input_disc_data(input_line)
        disc.do_simple_defragmentation()
        return disc.calculate_checksum()

    def run_part_two(self):
        return "---"


def parse_input_disc_data(input_line: str) -> Disc:
    disc = Disc()
    next_is_data_block = True
    next_data_block_id = 0

    for char in input_line:
        block_length = int(char)
        if next_is_data_block:
            for _ in range(block_length):
                disc.blocks.append(Block(type=BlockType.DATA, id=next_data_block_id))
            next_is_data_block = False
            next_data_block_id += 1
        else:
            for _ in range(block_length):
                disc.blocks.append(Block(type=BlockType.EMPTY))
            next_is_data_block = True

    return disc
