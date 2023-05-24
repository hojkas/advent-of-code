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
        print(f"Originally caves: {len(self.caves)}")
        self.caves = [cave for cave in self.caves if not cave.useless]
        print(f"Filtered caves: {len(self.caves)}")


def part_one(cave_map: CaveMap):
    starting_cave = [c for c in cave_map.caves if c.name == "AA"][0]
    paths = [([starting_cave], 0, 0)]
    total_pressure_releases = []
    while len(paths) != 0:
        path, minute, pressure_released = paths.pop(-1)
        current_cave = path[-1]
        not_explored_cave_distances = {cave: distance
                                       for cave, distance in current_cave.cave_distances.items() if cave not in path}

        # last cave
        if len(not_explored_cave_distances) == 0 or minute >= 30:
            total_pressure_releases.append(pressure_released)
            continue

        # not last cave
        for cave, distance in not_explored_cave_distances.items():
            temp_minute = minute + distance + 1
            if temp_minute > 30:
                total_pressure_releases.append(pressure_released)
                continue
            temp_pressure_released = pressure_released + cave.flow * (30 - temp_minute)
            new_path = path.copy()
            new_path.append(cave)
            paths.append((new_path, temp_minute, temp_pressure_released))

    total_pressure_releases.sort()
    return total_pressure_releases[-1]


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        cave_map = CaveMap(self.input_loader.load_input_array("\n"))
        result = part_one(cave_map)
        return result

    def run_part_two(self):
        return "---"
