from dataclasses import dataclass, field
from enum import StrEnum
from typing import Self

from helpers import InputLoader
from lib.abstract_day import AbstractDay

from lib.models import GenericMapField, GenericMapRepresentation, Direction

TURN_COST = 1000
MOVE_COST = 1

def get_default_best_paths_to_position() -> dict[Direction, int | None]:
    return {
        Direction.UP: None,
        Direction.DOWN: None,
        Direction.LEFT: None,
        Direction.RIGHT: None,
    }

class FieldType(StrEnum):
    WALL = "#"
    EMPTY = "."
    END = "E"
    START = "S"

@dataclass
class Field(GenericMapField):
    type: FieldType
    best_paths_to_position: dict[Direction, int | None] = field(default_factory=get_default_best_paths_to_position)

    @property
    def is_empty(self):
        return self.type != FieldType.WALL

    @property
    def is_start(self):
        return self.type == FieldType.START

    @property
    def is_end(self):
        return self.type == FieldType.END

    @property
    def best_score(self):
        try:
            return min([score for score in self.best_paths_to_position.values() if score is not None])
        except ValueError:
            return None

    def is_best_score_so_far(self, direction: Direction, current_score: int) -> bool:
        return self.best_paths_to_position[direction] is None or current_score < self.best_paths_to_position[direction]

    def mark_new_best_score_so_far(self, direction: Direction, current_score: int) -> None:
        self.best_paths_to_position[direction] = current_score


@dataclass
class Reindeer(GenericMapField):
    direction: Direction
    score: int = 0

    def create_turned_copy(self, new_direction: Direction, number_of_turns: int = 1) -> Self:
        return Reindeer(
            row=self.row,
            col=self.col,
            direction=new_direction,
            score=self.score + number_of_turns * TURN_COST
        )

    def move_forward(self, direction: Direction) -> None:
        self.row += direction.value[0]
        self.col += direction.value[1]
        self.score += MOVE_COST


@dataclass
class RaceMap(GenericMapRepresentation[Field]):
    fields: list[list[Field]]
    start_field: Field
    end_field: Field
    racing_reindeers: list[Reindeer]

    def get_reindeers_field(self, reindeer: Reindeer) -> Field:
        return self.fields[reindeer.row][reindeer.col]

    def _can_move_in_direction(self, reindeer: Reindeer, new_direction: Direction) -> bool:
        return not self.get_next_field_in_direction(
            self.get_reindeers_field(reindeer), new_direction
        ).type.value == FieldType.WALL

    def can_move_forward(self, reindeer: Reindeer) -> bool:
        return self._can_move_in_direction(reindeer, reindeer.direction)

    def can_move_right(self, reindeer: Reindeer) -> bool:
        return self._can_move_in_direction(reindeer, reindeer.direction.next_clockwise_cardinal)

    def can_move_left(self, reindeer: Reindeer) -> bool:
        return self._can_move_in_direction(reindeer, reindeer.direction.next_counter_clockwise_cardinal)

    def fetch_move_and_split_reindeer(self) -> None:
        reindeer = self.racing_reindeers.pop()

        if not self.can_move_forward(reindeer):
            return  # reindeer copy ends here

        reindeer.move_forward(reindeer.direction)
        self.resolve_reindeer_after_move_or_turn(reindeer, priority=True)

        # resolve possible right turning reindeer
        if self.can_move_right(reindeer):
            right_turned_reindeer = reindeer.create_turned_copy(reindeer.direction.next_clockwise_cardinal)
            self.resolve_reindeer_after_move_or_turn(right_turned_reindeer)

        # resolve possible left turning reindeer
        if self.can_move_left(reindeer):
            left_turned_reindeer = reindeer.create_turned_copy(reindeer.direction.next_counter_clockwise_cardinal)
            self.resolve_reindeer_after_move_or_turn(left_turned_reindeer)

    def resolve_reindeer_after_move_or_turn(self, reindeer: Reindeer, priority: bool = False) -> None:
        reindeer_field = self.get_reindeers_field(reindeer)
        if not reindeer_field.is_best_score_so_far(reindeer.direction, reindeer.score):
            return  # better reindeer ran through before this
        reindeer_field.mark_new_best_score_so_far(reindeer.direction, reindeer.score)

        if self.fields[reindeer.row][reindeer.col].is_end:
            return  # reindeer finished after marking this great score

        if priority:
            self.racing_reindeers.insert(0, reindeer)
        else:
            self.racing_reindeers.append(reindeer)  # reindeer is still in game

    def gather_reindeer_positions(self) -> dict[tuple[int, int], list[Direction]]:
        reindeer_positions = {}
        for reindeer in self.racing_reindeers:
            reindeer_positions.setdefault((reindeer.row, reindeer.col), [])
            reindeer_positions[(reindeer.row, reindeer.col)].append(reindeer.direction)
        return reindeer_positions

    def print_map(self):
        reindeer_positions = self.gather_reindeer_positions()

        for row in range(self.row_count):
            for col in range(self.col_count):
                char_to_print = self.fields[row][col].type.value
                if (row, col) in reindeer_positions:
                    if len(reindeer_positions[(row, col)]) > 1:
                        char_to_print = len(reindeer_positions[(row, col)])
                    else:
                        direction = reindeer_positions[(row, col)][0]
                        char_to_print = {
                            Direction.UP: "^", Direction.DOWN: "v", Direction.LEFT: "<", Direction.RIGHT: ">"
                        }[direction]
                print(char_to_print, end="")
            print()

class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: InputLoader | None = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_array = self.input_loader.load_input_array(item_separator="\n")
        race_map = load_race_map(input_array)
        while len(race_map.racing_reindeers) > 0:
            race_map.fetch_move_and_split_reindeer()

        return race_map.end_field.best_score

    def run_part_two(self):
        return "---"


def load_race_map(input_array: list[str]) -> RaceMap:
    fields = []
    original_reindeer = None
    start_field = None
    end_field = None

    for row_id, row in enumerate(input_array):
        field_row = []
        for col_id, char in enumerate(row):
            if char == "S":
                original_reindeer = Reindeer(row=row_id, col=col_id, direction=Direction.RIGHT)
                this_field = Field(row=row_id, col=col_id, type=FieldType.START)
                field_row.append(this_field)
                start_field = this_field
            elif char == "E":
                this_field = Field(row=row_id, col=col_id, type=FieldType.END)
                field_row.append(this_field)
                end_field = this_field
            else:
                field_row.append(Field(row=row_id, col=col_id, type=FieldType(char)))
        fields.append(field_row)

    reindeers = [
        original_reindeer,
        original_reindeer.create_turned_copy(Direction.UP),
        original_reindeer.create_turned_copy(Direction.DOWN),
        original_reindeer.create_turned_copy(Direction.LEFT, number_of_turns=2),
    ]

    return RaceMap(fields=fields, start_field=start_field, end_field=end_field, racing_reindeers=reindeers)
