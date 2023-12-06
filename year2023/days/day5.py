from enum import Enum
from typing import Union, Optional
from dataclasses import dataclass, field

from lib.abstract_day import AbstractDay
from helpers import InputLoader


class ItemType(Enum):
    SEED = 1
    SOIL = 2
    FERTILIZER = 3
    WATER = 4
    LIGHT = 5
    TEMPERATURE = 6
    HUMIDITY = 7
    LOCATION = 8


@dataclass
class Seed:
    seed_id: int
    soil_id: Optional[int] = None
    fertilizer_id: Optional[int] = None
    water_id: Optional[int] = None
    light_id: Optional[int] = None
    temperature_id: Optional[int] = None
    humidity_id: Optional[int] = None
    location_id: Optional[int] = None


@dataclass
class ConversionItem:
    source_start: int
    source_end: int
    destination_start: int
    destination_end: int
    destination_offset: int


@dataclass
class ConversionMap:
    source_type: ItemType
    destination_type: ItemType
    conversions: list[ConversionItem] = field(default_factory=list)


@dataclass
class ConversionMaps:
    seed_to_soil: ConversionMap
    soil_to_fertilizer: ConversionMap
    fertilizer_to_water: ConversionMap
    water_to_light: ConversionMap
    light_to_temperature: ConversionMap
    temperature_to_humidity: ConversionMap
    humidity_to_location: ConversionMap


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_list = self.input_loader.load_input_array(item_separator="\n\n")
        seeds = load_seeds(input_list[0])
        conversion_maps = load_conversion_maps(input_list[1:])
        fill_seeds_information(seeds, conversion_maps)
        result = find_lowest_location(seeds)
        return result

    def run_part_two(self):
        return "---"


def load_seeds(line_with_seeds: str) -> list[Seed]:
    seeds = []
    for seed_string in line_with_seeds.split(" ")[1:]:
        seeds.append(Seed(int(seed_string)))
    return seeds


def fill_seeds_information(seeds: list[Seed], conversion_maps: ConversionMaps) -> None:
    for seed in seeds:
        fill_seed_information(seed, conversion_maps)


def fill_seed_information(seed: Seed, conversion_maps: ConversionMaps) -> None:
    seed.soil_id = get_conversion(seed.seed_id, conversion_maps.seed_to_soil)
    seed.fertilizer_id = get_conversion(seed.soil_id, conversion_maps.soil_to_fertilizer)
    seed.water_id = get_conversion(seed.fertilizer_id, conversion_maps.fertilizer_to_water)
    seed.light_id = get_conversion(seed.water_id, conversion_maps.water_to_light)
    seed.temperature_id = get_conversion(seed.light_id, conversion_maps.light_to_temperature)
    seed.humidity_id = get_conversion(seed.temperature_id, conversion_maps.temperature_to_humidity)
    seed.location_id = get_conversion(seed.humidity_id, conversion_maps.humidity_to_location)


def get_conversion(source_id: int, conversion_map: ConversionMap):
    for conversion_item in conversion_map.conversions:
        if conversion_item.source_start <= source_id <= conversion_item.source_end:
            return source_id + conversion_item.destination_offset
    return source_id


def load_conversion_maps(input_list: list[str]) -> ConversionMaps:
    return ConversionMaps(
        seed_to_soil=load_conversion_map(input_list[0], ItemType.SEED, ItemType.SOIL),
        soil_to_fertilizer=load_conversion_map(input_list[1], ItemType.SOIL, ItemType.FERTILIZER),
        fertilizer_to_water=load_conversion_map(input_list[2], ItemType.FERTILIZER, ItemType.WATER),
        water_to_light=load_conversion_map(input_list[3], ItemType.WATER, ItemType.LIGHT),
        light_to_temperature=load_conversion_map(input_list[4], ItemType.LIGHT, ItemType.TEMPERATURE),
        temperature_to_humidity=load_conversion_map(input_list[5], ItemType.TEMPERATURE, ItemType.HUMIDITY),
        humidity_to_location=load_conversion_map(input_list[6], ItemType.HUMIDITY, ItemType.LOCATION)
    )


def load_conversion_map(string_conversion_map: str, source_type: ItemType, destination_type: ItemType
                        ) -> ConversionMap:
    conversion_map = ConversionMap(source_type=source_type, destination_type=destination_type)
    conversion_lines = string_conversion_map.split("\n")[1:]
    for line in conversion_lines:
        destination_start, source_start, number_range = (int(x) for x in line.split(" "))
        conversion_map.conversions.append(ConversionItem(
            source_start=source_start,
            source_end=(source_start + number_range - 1),
            destination_start=destination_start,
            destination_end=(destination_start + number_range - 1),
            destination_offset=(destination_start - source_start)
        ))
    return conversion_map


def find_lowest_location(seeds: list[Seed]) -> int:
    location_ids = [seed.location_id for seed in seeds]
    location_ids.sort()
    return location_ids[0]
