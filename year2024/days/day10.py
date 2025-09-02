from dataclasses import dataclass, field
from typing import Optional, cast

from helpers import InputLoader
from lib.abstract_day import AbstractDay
from lib.exceptions import OutOfBoundsError
from lib.models import GenericMapField, GenericMapRepresentationDeprecated, Direction


@dataclass
class MapField(GenericMapField):
    height: int
    can_reach_peaks_basic: list['MapField'] = field(default_factory=list)
    peak_reachability_score: int = 0

    def add_reachable_peak(self, peak):
        self.can_reach_peaks_basic.append(peak)

    def add_reachable_peaks(self, peaks: list['MapField']):
        for peak in peaks:
            if peak not in self.can_reach_peaks_basic:
                self.can_reach_peaks_basic.append(peak)

    def is_peak(self):
        return self.height == 9

    def is_trail_head(self):
        return self.height == 0


@dataclass
class TrailMap(GenericMapRepresentationDeprecated):
    fields: list[list[MapField]]
    trail_heads: list[MapField] = field(default_factory=list)
    peaks: list[MapField] = field(default_factory=list)

    def __init__(self, fields: list[list[MapField]]) -> None:
        super().__init__(fields)

    def fill_peak_reachability(self) -> None:
        current_layer_to_continue = self.peaks.copy()
        current_layer_level = 9
        while current_layer_level > 0:
            current_layer_to_continue = self._fill_next_layer_peak_reachability(
                current_layer_to_continue, current_layer_level
            )
            current_layer_level -= 1

    def _fill_next_layer_peak_reachability(self, current_layer: list[MapField], current_level: int) -> list[MapField]:
        future_layer = []
        sought_level = current_level - 1

        for map_field in current_layer:
            for neighbouring_peak_direction in Direction.get_cardinal():
                try:
                    neighbouring_peak = cast(
                        MapField,
                        self.get_next_field_in_direction(current_field=map_field, direction=neighbouring_peak_direction)
                    )
                    if neighbouring_peak.height == sought_level:
                        if neighbouring_peak not in future_layer:
                            future_layer.append(neighbouring_peak)
                        neighbouring_peak.add_reachable_peaks(map_field.can_reach_peaks_basic)
                        neighbouring_peak.peak_reachability_score += map_field.peak_reachability_score
                except OutOfBoundsError:
                    pass  # no peak next to it, nothing to check

        return future_layer


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        trail_map = parse_trail_map(self.input_loader.load_input_array("\n"))
        trail_map.fill_peak_reachability()
        return sum(len(f.can_reach_peaks_basic) for f in trail_map.trail_heads)

    def run_part_two(self):
        trail_map = parse_trail_map(self.input_loader.load_input_array("\n"))
        trail_map.fill_peak_reachability()
        return sum(f.peak_reachability_score for f in trail_map.trail_heads)


def parse_trail_map(lines: list[str]) -> TrailMap:
    trail_map_fields = []
    trail_map_trail_heads = []
    trail_map_peaks = []

    for row_id, line in enumerate(lines):
        line_fields = []
        for col_id, char in enumerate(line):
            height = int(char)
            map_field = MapField(height=height, row=row_id, col=col_id)
            line_fields.append(map_field)
            if height == 0:
                trail_map_trail_heads.append(map_field)
            elif height == 9:
                map_field.can_reach_peaks_basic.append(map_field)  # add self as reachable
                map_field.peak_reachability_score = 1  # can reach exactly one peak - itself
                trail_map_peaks.append(map_field)
        trail_map_fields.append(line_fields)

    trail_map = TrailMap(fields=trail_map_fields)
    trail_map.trail_heads = trail_map_trail_heads
    trail_map.peaks = trail_map_peaks
    return trail_map
