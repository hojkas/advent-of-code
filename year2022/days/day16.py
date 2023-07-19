from typing import Union
from abstract_day import AbstractDay
from helpers import InputLoader, regex_extract_multiple


class Cave:
    def __init__(self, name: str, flow: int, tunnels: list[str]):
        self.flow: int = flow
        self.useless: bool = (flow == 0 and name != "AA")
        self.name: str = name
        self.tunnels: list[str] = tunnels
        self.connected_caves: list[Cave] = []
        self.cave_distances: dict[Cave, int] = {}

    def __repr__(self):
        return self.name

    def __str__(self):
        connected_cave_names = [c.name for c in self.connected_caves]
        distances = [(c.name, distance) for c, distance in self.cave_distances.items()]
        return f"{self.name} [{self.flow}] - {connected_cave_names} {distances}"


class CaveMap:
    def __init__(self, cave_map_string_array):
        self.caves: list[Cave] = []
        for cave_string in cave_map_string_array:
            info = regex_extract_multiple(r"Valve (.*?) has flow rate=(\d*?); tunnels? leads? to valves? (.*?)$",
                                          cave_string, 3)
            name = info[0]
            flow_rate = int(info[1])
            tunnels = info[2].split(", ")
            self.caves.append(Cave(name, flow_rate, tunnels))
        self._load_connected_caves()
        self._count_distances_for_all_caves()
        self._filter_useless_caves()

    def _load_connected_caves(self):
        for cave in self.caves:
            for tunnel_string in cave.tunnels:
                cave.connected_caves.append([c for c in self.caves if c.name == tunnel_string][0])

    def _count_distances_for_all_caves(self):
        for starting_cave in self.caves:
            for end_cave in self.caves:
                if (starting_cave != end_cave
                        and not starting_cave.useless
                        and not end_cave.useless
                        and end_cave not in starting_cave.cave_distances.keys()):
                    self._count_cave_distance(starting_cave, end_cave)

    @staticmethod
    def _count_cave_distance(starting_cave, end_cave):
        shortest: Union[None, int] = None
        paths = [[starting_cave]]
        while len(paths) != 0:
            path = paths.pop(0)
            current_cave = path[-1]

            # reached the cave
            if current_cave == end_cave:
                if shortest is None or len(path) - 1 < shortest:
                    shortest = len(path) - 1
                continue

            # not the end cave
            for cave in current_cave.connected_caves:
                if cave not in path:
                    new_path = path.copy()
                    new_path.append(cave)
                    paths.append(new_path)
        starting_cave.cave_distances[end_cave] = shortest
        end_cave.cave_distances[starting_cave] = shortest

    def _filter_useless_caves(self):
        self.caves = [cave for cave in self.caves if not cave.useless]


def part_one(cave_map: CaveMap, max_minutes: int):
    starting_cave = [c for c in cave_map.caves if c.name == "AA"][0]
    paths = [([starting_cave], 0, 0)]
    total_pressure_releases = []
    while len(paths) != 0:
        path, minute, pressure_released = paths.pop(-1)
        current_cave = path[-1]
        not_explored_cave_distances = {cave: distance
                                       for cave, distance in current_cave.cave_distances.items() if cave not in path}

        # last cave
        if len(not_explored_cave_distances) == 0 or minute >= max_minutes:
            total_pressure_releases.append(pressure_released)
            continue

        # not last cave
        for cave, distance in not_explored_cave_distances.items():
            temp_minute = minute + distance + 1
            if temp_minute > max_minutes:
                total_pressure_releases.append(pressure_released)
                continue
            temp_pressure_released = pressure_released + cave.flow * (max_minutes - temp_minute)
            new_path = path.copy()
            new_path.append(cave)
            paths.append((new_path, temp_minute, temp_pressure_released))

    total_pressure_releases.sort()
    return total_pressure_releases[-1]


class Actor:
    def __init__(self, current_cave):
        self.cave = current_cave
        self.on_route = False
        self.time_till_arrival = 0

    def depart_for(self, cave, distance):
        self.cave = cave
        self.on_route = True
        self.time_till_arrival = distance

    def pass_minute(self):
        if self.on_route:
            self.time_till_arrival -= 1
            if self.time_till_arrival == 0:
                self.on_route = False

    def __copy__(self):
        new = Actor(self.cave)
        new.on_route = self.on_route
        new.time_till_arrival = self.time_till_arrival
        return new


class PossiblePath:
    def __init__(self, starting_cave, time_left):
        self.starting_cave = starting_cave
        self.explored_caves = [starting_cave]
        self.opened_caves = [starting_cave]
        self.pressure_released = 0
        self.person = Actor(starting_cave)
        self.elephant = Actor(starting_cave)
        self.time_left = time_left

    def __copy__(self):
        new = PossiblePath(self.starting_cave, self.time_left)
        new.explored_caves = self.explored_caves.copy()
        new.person = self.person.__copy__()
        new.elephant = self.elephant.__copy__()
        new.pressure_released = self.pressure_released
        new.opened_caves = self.opened_caves.copy()
        return new


def find_possible_paths(curr_path, unexplored_paths, finished_paths, cave_map):
    while curr_path.person.on_route and curr_path.elephant.on_route:
        curr_path.time_left -= 1
        curr_path.person.pass_minute()
        curr_path.elephant.pass_minute()

    # Time is up
    if curr_path.time_left <= 0:
        finished_paths.append(curr_path)
        return

    prep_paths = []

    if not curr_path.person.on_route:
        # turn the valve if not yet done
        if curr_path.person.cave not in curr_path.opened_caves:
            pass

        # or explore more
        for cave in cave_map:
            if cave in curr_path.explored_caves:
                continue
            new_path = curr_path.__copy__()
            new_path.explored_caves.append(cave)
            new_path.person.depart_for(cave, curr_path.person.cave.cave_distances[cave])



def part_two(cave_map: CaveMap, max_minutes: int):
    starting_cave = [c for c in cave_map.caves if c.name == "AA"][0]
    unexplored_paths = [PossiblePath(starting_cave, max_minutes)]
    finished_paths = []
    while len(unexplored_paths) != 0:
        curr_path = unexplored_paths.pop(0)
        find_possible_paths(curr_path, unexplored_paths, finished_paths, cave_map)

    return max([path.pressure_released for path in finished_paths])


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        cave_map = CaveMap(self.input_loader.load_input_array("\n"))
        result = part_one(cave_map, 30)
        return result

    def run_part_two(self):
        cave_map = CaveMap(self.input_loader.load_input_array("\n"))
        result = part_two(cave_map, 26)
        return "---"
