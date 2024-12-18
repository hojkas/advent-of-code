from dataclasses import dataclass, field
from typing import Optional, cast

from helpers import InputLoader
from lib.abstract_day import AbstractDay
from lib.models import GenericMapField, GenericMapRepresentation, Direction


@dataclass
class Fence:
    row: int
    col: int
    side: Direction


@dataclass
class FarmField(GenericMapField):
    name: Optional[str] = None
    area: Optional['Area'] = None


@dataclass
class Area:
    id: int
    name: str
    fields: list[FarmField] = field(default_factory=list)
    fences: list[Fence] = field(default_factory=list)


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
        return "---"


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
        neighbours = farm.get_cardinal_neighbouring_fields(current_field=current_field, include_empty=True)
        for direction, neighbour in neighbours.items():
            neighbour = cast(FarmField, neighbour)  # for typing comfort
            if neighbour is None or neighbour.name != current_field.name:
                # different field or side of map
                new_area.fences.append(Fence(row=current_field.row, col=current_field.col, side=direction))
            elif neighbour in new_area.fields or neighbour in flood_match_fields:
                pass  # neighbour already processed/in queue
            else:
                new_area.fields.append(neighbour)
                flood_match_fields.append(neighbour)
                farm.unmatched_fields.remove(neighbour)
                neighbour.area = new_area

    farm.areas.append(new_area)
