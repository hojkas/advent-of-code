from enum import Enum
from typing import Union, Optional
from dataclasses import dataclass, field

from lib.abstract_day import AbstractDay
from lib.exceptions import RunException
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


ITEM_TYPES_ASCENDING = [
    ItemType.SEED,
    ItemType.SOIL,
    ItemType.FERTILIZER,
    ItemType.WATER,
    ItemType.LIGHT,
    ItemType.TEMPERATURE,
    ItemType.HUMIDITY,
    ItemType.LOCATION,
]

ITEM_TYPES_DESCENDING = [
    ItemType.LOCATION,
    ItemType.HUMIDITY,
    ItemType.TEMPERATURE,
    ItemType.LIGHT,
    ItemType.WATER,
    ItemType.FERTILIZER,
    ItemType.SOIL,
    ItemType.SEED
]


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
class SeedRangeItem:
    first: int
    last: int


@dataclass
class SeedRange:
    items: dict[ItemType, Optional[SeedRangeItem]]

    def __init__(self):
        self.items = {
            ItemType.LOCATION: None,
            ItemType.HUMIDITY: None,
            ItemType.TEMPERATURE: None,
            ItemType.LIGHT: None,
            ItemType.WATER: None,
            ItemType.FERTILIZER: None,
            ItemType.SOIL: None,
            ItemType.SEED: None,
        }


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

    def get_by_type(self, source_item_type: ItemType, destination_item_type: ItemType):
        if source_item_type == ItemType.SEED and destination_item_type == ItemType.SOIL:
            return self.seed_to_soil
        if source_item_type == ItemType.SOIL and destination_item_type == ItemType.FERTILIZER:
            return self.soil_to_fertilizer
        if source_item_type == ItemType.FERTILIZER and destination_item_type == ItemType.WATER:
            return self.fertilizer_to_water
        if source_item_type == ItemType.WATER and destination_item_type == ItemType.LIGHT:
            return self.water_to_light
        if source_item_type == ItemType.LIGHT and destination_item_type == ItemType.TEMPERATURE:
            return self.light_to_temperature
        if source_item_type == ItemType.TEMPERATURE and destination_item_type == ItemType.HUMIDITY:
            return self.temperature_to_humidity
        if source_item_type == ItemType.HUMIDITY and destination_item_type == ItemType.LOCATION:
            return self.humidity_to_location
        raise RunException(f"Unknown type {source_item_type} to {destination_item_type}")


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
        input_list = self.input_loader.load_input_array(item_separator="\n\n")
        seed_ranges = load_seed_ranges(input_list[0])
        conversion_maps = load_conversion_maps(input_list[1:])
        filled_seed_ranges = fill_seed_ranges_information(seed_ranges, conversion_maps)
        result = find_lowest_location_in_seed_ranges(filled_seed_ranges)
        return result


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


def get_conversion_offset(source_id: int, conversion_map: ConversionMap) -> int:
    for conversion_item in conversion_map.conversions:
        if conversion_item.source_start <= source_id <= conversion_item.source_end:
            return conversion_item.destination_offset
    return 0


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


def load_seed_ranges(input_line: str) -> list[SeedRange]:
    seed_ranges = []
    input_array = input_line.split(" ")[1:]
    for i in range(0, len(input_array), 2):
        new_seed_range = SeedRange()
        first_id = int(input_array[i])
        last_id = first_id + int(input_array[i + 1]) - 1
        new_seed_range.items[ItemType.SEED] = SeedRangeItem(first=first_id, last=last_id)
        seed_ranges.append(new_seed_range)
    return seed_ranges


def fill_seed_ranges_information(original_seed_ranges: list[SeedRange],
                                 conversion_maps: ConversionMaps) -> list[SeedRange]:
    new_seed_ranges = []
    for seed_range in original_seed_ranges:
        fill_seed_range_information(seed_range, new_seed_ranges, ItemType.SEED, ItemType.SOIL, conversion_maps)
    return new_seed_ranges


def fill_seed_range_information(seed_range: SeedRange,
                                finished_seed_ranges: list[SeedRange],
                                item_type_already_filled: ItemType,
                                item_type_to_fill: ItemType,
                                conversion_maps: ConversionMaps) -> None:
    future_item_type = get_next_item_type(item_type_to_fill)
    # find points where the conversion changes within the range
    real_cutoff_points = find_range_cutoff_points(conversion_maps, item_type_already_filled, item_type_to_fill,
                                                  seed_range)
    real_cutoff_points.sort()
    # split the range by those points
    new_seed_ranges_to_explore = cut_range_by_points(seed_range, real_cutoff_points, item_type_already_filled)

    # update seed ranges - calculate the value of next layer ids
    calculate_next_item_type_layer(new_seed_ranges_to_explore, item_type_already_filled, item_type_to_fill,
                                   conversion_maps)

    # decide on next steps
    if future_item_type is None:  # this is the last layer
        for new_seed_range in new_seed_ranges_to_explore:
            finished_seed_ranges.append(new_seed_range)
            return

    # not the last layer - run this function again for each new range created
    for new_seed_range in new_seed_ranges_to_explore:
        fill_seed_range_information(
            new_seed_range, finished_seed_ranges, item_type_to_fill, future_item_type, conversion_maps)


def calculate_next_item_type_layer(new_seed_ranges_to_explore, item_type_already_filled, item_type_to_fill,
                                   conversion_maps):
    for new_seed_range in new_seed_ranges_to_explore:
        conversion_offset_to_apply = get_conversion_offset(
            new_seed_range.items[item_type_already_filled].first,
            conversion_maps.get_by_type(item_type_already_filled, item_type_to_fill))
        conversion_to_apply_doublecheck = get_conversion_offset(
            new_seed_range.items[item_type_already_filled].last,
            conversion_maps.get_by_type(item_type_already_filled, item_type_to_fill))
        if conversion_offset_to_apply != conversion_to_apply_doublecheck:
            raise RunException("Should have been the same conversion rule")
        new_seed_range.items[item_type_to_fill] = SeedRangeItem(
            first=new_seed_range.items[item_type_already_filled].first + conversion_offset_to_apply,
            last=new_seed_range.items[item_type_already_filled].last + conversion_offset_to_apply
        )


def cut_range_by_points(seed_range, real_cutoff_points, item_type_already_filled):
    new_seed_ranges_to_explore = []
    current_range = seed_range
    last_cutoff_point = None
    for cutoff_point in real_cutoff_points:
        if cutoff_point == last_cutoff_point:
            continue
        last_cutoff_point = cutoff_point
        first_range, second_range = split_seed_range(current_range, cutoff_point, item_type_already_filled)
        new_seed_ranges_to_explore.append(first_range)
        current_range = second_range
    new_seed_ranges_to_explore.append(current_range)  # only this happens when no cutoff points present
    return new_seed_ranges_to_explore


def find_range_cutoff_points(conversion_maps, item_type_already_filled, item_type_to_fill, seed_range):
    possible_cutoff_points = [
                                 c.source_start - 1  # - 1 because we want to cut off after the element before it
                                 for c in
                                 conversion_maps.get_by_type(item_type_already_filled, item_type_to_fill).conversions
                             ] + [
                                 c.source_end
                                 for c in
                                 conversion_maps.get_by_type(item_type_already_filled, item_type_to_fill).conversions
                             ]
    real_cutoff_points = []
    for possible_cutoff_point in possible_cutoff_points:
        if (seed_range.items[item_type_already_filled].first
                <= possible_cutoff_point
                < seed_range.items[item_type_already_filled].last):
            real_cutoff_points.append(possible_cutoff_point)
    return real_cutoff_points


def get_next_item_type(current_item_type: ItemType) -> Optional[ItemType]:
    for i in range(len(ITEM_TYPES_ASCENDING) - 1):
        if current_item_type == ITEM_TYPES_ASCENDING[i]:
            return ITEM_TYPES_ASCENDING[i + 1]
    return None


def split_seed_range(seed_range: SeedRange, cut_after_id: int, cut_on_type: ItemType) -> (SeedRange, SeedRange):
    cut_after_offset = 0
    cutting_started = False
    first_seed_range = SeedRange()
    second_seed_range = SeedRange()

    for item_type in ITEM_TYPES_DESCENDING:
        if cutting_started or cut_on_type == item_type:
            if not cutting_started:
                if not (seed_range.items[item_type].first <= cut_after_id < seed_range.items[item_type].last):
                    raise RunException(f"Invalid cut position. Cut_after_id: {cut_after_id}, "
                                       f"cut_on_type: {cut_on_type}, seed_range: {seed_range}")
                cutting_started = True
                cut_after_offset = cut_after_id - seed_range.items[item_type].first
            first_seed_range.items[item_type] = SeedRangeItem(
                first=seed_range.items[item_type].first,
                last=seed_range.items[item_type].first + cut_after_offset)
            second_seed_range.items[item_type] = SeedRangeItem(
                first=seed_range.items[item_type].first + cut_after_offset + 1,
                last=seed_range.items[item_type].last)

    return first_seed_range, second_seed_range


def find_lowest_location_in_seed_ranges(seed_ranges: list[SeedRange]) -> int:
    lowest = None
    for seed_range in seed_ranges:
        if not lowest or seed_range.items[ItemType.LOCATION].first < lowest:
            lowest = seed_range.items[ItemType.LOCATION].first
    return lowest
