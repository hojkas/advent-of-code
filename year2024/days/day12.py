from dataclasses import dataclass, field
from functools import cache
from typing import Optional, cast

from helpers import InputLoader
from lib.abstract_day import AbstractDay
from lib.models import GenericMapField, GenericMapRepresentation, Direction


@dataclass
class FenceField:
    row: int
    col: int
    side: Direction


@dataclass
class HorizontalFence:
    lies_before_row: int
    runs_across_col: int
    topside_is_out: bool


@dataclass
class VerticalFence:
    lies_before_col: int
    runs_across_row: int
    rightside_is_out: bool


@dataclass
class FarmField(GenericMapField):
    name: Optional[str] = None
    area: Optional['Area'] = None


@dataclass
class Area:
    id: int
    name: str
    fields: list[FarmField] = field(default_factory=list)
    fences: list[FenceField] = field(default_factory=list)
    horizontal_fences: dict[int, list[HorizontalFence]] = field(default_factory=dict)
    vertical_fences: dict[int, list[VerticalFence]] = field(default_factory=dict)

    @property
    def number_of_sides(self) -> int:
        if len(self.horizontal_fences) == 0 or len(self.vertical_fences) == 0:
            raise RuntimeError(f"Fences were not categorized! Run categorize_fences() first.")

        count = 0
        for horizontal_fences_in_a_row in self.horizontal_fences.values():
            count += self.count_continous_fence_sequence(
                [(f.runs_across_col, f.topside_is_out) for f in horizontal_fences_in_a_row]
            )
        for vertical_fences_in_a_col in self.vertical_fences.values():
            count += self.count_continous_fence_sequence(
                [(f.runs_across_row, f.rightside_is_out) for f in vertical_fences_in_a_col]
            )

        return count

    @staticmethod
    def count_continous_fence_sequence(affiliated_numbers: list[tuple[int, bool]]) -> int:
        affiliated_sorted_numbers = sorted(affiliated_numbers, key=lambda x: x[0])
        sequence_count = 0
        expected_number = None
        expected_affinity: Optional[bool] = None

        for number, affinity in affiliated_sorted_numbers:
            if number == expected_number and affinity == expected_affinity:
                expected_number += 1
            else:
                sequence_count += 1
                expected_number = number + 1
                expected_affinity = affinity

        return sequence_count

    def categorize_fences(self) -> None:
        for fence in self.fences:
            if fence.side == Direction.UP:
                self.add_horizontal_fence(runs_across_col=fence.col, lies_before_row=fence.row, topside_is_out=True)
            if fence.side == Direction.DOWN:
                self.add_horizontal_fence(runs_across_col=fence.col, lies_before_row=fence.row + 1, topside_is_out=False)
            if fence.side == Direction.LEFT:
                self.add_vertical_fence(runs_across_row=fence.row, lies_before_col=fence.col, rightside_is_out=False)
            if fence.side == Direction.RIGHT:
                self.add_vertical_fence(runs_across_row=fence.row, lies_before_col=fence.col + 1, rightside_is_out=True)

    def add_horizontal_fence(self, runs_across_col: int, lies_before_row: int, topside_is_out: bool) -> None:
        horizontal_fence = HorizontalFence(
            runs_across_col=runs_across_col, lies_before_row=lies_before_row, topside_is_out=topside_is_out
        )
        if lies_before_row in self.horizontal_fences:
            self.horizontal_fences[lies_before_row].append(horizontal_fence)
        else:
            self.horizontal_fences[lies_before_row] = [horizontal_fence]

    def add_vertical_fence(self, runs_across_row: int, lies_before_col: int, rightside_is_out: bool) -> None:
        vertical_fence = VerticalFence(
            runs_across_row=runs_across_row, lies_before_col=lies_before_col, rightside_is_out=rightside_is_out
        )
        if lies_before_col in self.vertical_fences:
            self.vertical_fences[lies_before_col].append(vertical_fence)
        else:
            self.vertical_fences[lies_before_col] = [vertical_fence]


@dataclass
class Farm(GenericMapRepresentation):
    fields: list[list[FarmField]] = field(default_factory=list)
    areas: list[Area] = field(default_factory=list)
    unmatched_fields: list[FarmField] = field(default_factory=list)


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        farm = parse_farm(self.input_loader.load_input_array("\n"))
        return sum(len(area.fences) * len(area.fields) for area in farm.areas)

    def run_part_two(self):
        farm = parse_farm(self.input_loader.load_input_array("\n"))
        price = 0
        for area in farm.areas:
            area.categorize_fences()
            price += len(area.fields) * area.number_of_sides
        return price


def parse_farm(input_array: list[str]) -> Farm:
    farm = Farm()

    # load basic fields
    for row, line in enumerate(input_array):
        farm_row = []
        for col, char in enumerate(line):
            new_field = FarmField(name=char, row=row, col=col)
            farm_row.append(new_field)
            farm.unmatched_fields.append(new_field)
        farm.fields.append(farm_row)

    sort_fields_into_areas(farm)
    return farm


def sort_fields_into_areas(farm: Farm) -> None:
    while len(farm.unmatched_fields) > 0:
        field_to_area_match = farm.unmatched_fields.pop(0)
        create_area_from_one_field(field_to_area_match, farm)


def create_area_from_one_field(field_to_area_match: FarmField, farm: Farm) -> None:
    new_area = Area(name=field_to_area_match.name, id=len(farm.areas))
    new_area.fields.append(field_to_area_match)
    field_to_area_match.area = new_area

    flood_match_fields = [field_to_area_match]
    while len(flood_match_fields) > 0:
        current_field = flood_match_fields.pop(0)
        neighbours = farm.get_cardinal_neighbouring_fields(current_field=current_field, include_out_of_bounds=True)
        for direction, neighbour in neighbours.items():
            neighbour = cast(FarmField, neighbour)  # for typing comfort
            if neighbour is None or neighbour.name != current_field.name:
                # different field or side of map
                new_area.fences.append(FenceField(row=current_field.row, col=current_field.col, side=direction))
            elif neighbour in new_area.fields or neighbour in flood_match_fields:
                pass  # neighbour already processed/in queue
            else:
                new_area.fields.append(neighbour)
                flood_match_fields.append(neighbour)
                farm.unmatched_fields.remove(neighbour)
                neighbour.area = new_area

    farm.areas.append(new_area)
