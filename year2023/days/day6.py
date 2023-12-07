from typing import Optional
from dataclasses import dataclass, field

from lib.abstract_day import AbstractDay
from helpers import InputLoader


@dataclass
class Race:
    time: int
    distance_to_beat: int
    win_rev_up_count: int = 0


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_times_string, input_distances_string = self.input_loader.load_input_array(item_separator="\n")
        races = load_races(input_times_string, input_distances_string)
        calculate_win_rev_up_times(races)
        result = multiply_all_win_possibilites(races)
        return result

    def run_part_two(self):
        input_times_string, input_distances_string = self.input_loader.load_input_array(item_separator="\n")
        race = load_as_one_race(input_times_string, input_distances_string)
        calculate_win_rev_up_time(race)
        result = race.win_rev_up_count
        return result


def load_races(times_string: str, distances_string: str) -> list[Race]:
    races = []
    times = [int(x) for x in times_string.split(" ") if x and x != "Time:"]
    distances = [int(x) for x in distances_string.split(" ") if x and x != "Distance:"]
    for time, distance in zip(times, distances):
        races.append(Race(time=time, distance_to_beat=distance))
    return races


def load_as_one_race(times_string: str, distances_string: str) -> Race:
    times_string = times_string.replace(" ", "")
    distances_string = distances_string.replace(" ", "")
    return Race(
        time=int(times_string.split(":")[1]),
        distance_to_beat=int(distances_string.split(":")[1])
    )


def calculate_win_rev_up_times(races: list[Race]) -> None:
    for race in races:
        calculate_win_rev_up_time(race)


def calculate_win_rev_up_time(race: Race) -> None:
    sure_win_around = race.time // 2
    check_win_rev_up_time(race, sure_win_around + 1, 1)  # check more rev up
    check_win_rev_up_time(race, sure_win_around, -1)  # check less rev up


def check_win_rev_up_time(race: Race, win_rev_up_time: int, next_to_check_direction: int) -> None:
    for mass_check_chunk in [1000000, 100000, 10000, 1000, 100, 10]:
        next_value_after_chunk = win_rev_up_time + next_to_check_direction * mass_check_chunk
        if race_wins(race, next_value_after_chunk):
            race.win_rev_up_count += mass_check_chunk
            check_win_rev_up_time(race, next_value_after_chunk, next_to_check_direction)
            return

    # no chunk performed, go one by one
    if race_wins(race, win_rev_up_time):
        race.win_rev_up_count += 1
        check_win_rev_up_time(race, win_rev_up_time + next_to_check_direction, next_to_check_direction)


def race_wins(race: Race, rev_up_time) -> bool:
    time_left = race.time - rev_up_time
    return rev_up_time * time_left > race.distance_to_beat


def multiply_all_win_possibilites(races: list[Race]) -> int:
    product = 1
    for race in races:
        product *= race.win_rev_up_count
    return product

