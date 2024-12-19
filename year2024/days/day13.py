from dataclasses import dataclass, field
from typing import Optional

from helpers import InputLoader
from lib.abstract_day import AbstractDay


@dataclass
class Button:
    x_move: int
    y_move: int


@dataclass
class WinningMove:
    a_presses: int
    b_presses: int

    @property
    def price(self) -> int:
        return self.a_presses * 3 + self.b_presses


@dataclass
class ClawMachine:
    a_button: Button
    b_button: Button
    x_goal: int
    y_goal: int
    max_moves_limit: int = 100
    winning_moves: list[WinningMove] = field(default_factory=list)

    @property
    def cheapest_winning_move(self) -> Optional[WinningMove]:
        if len(self.winning_moves) == 0:
            return None
        cheapest_winning_move = self.winning_moves[0]
        for winning_move in self.winning_moves[1:]:
            if winning_move.price < cheapest_winning_move.price:
                cheapest_winning_move = winning_move
        return cheapest_winning_move

    def calculate_winning_moves(self) -> None:
        max_b_moves_on_x = self.x_goal // self.b_button.x_move
        max_b_moves_on_y = self.y_goal // self.b_button.y_move

        current_b_move_count = min(max_b_moves_on_x, max_b_moves_on_y)
        current_a_move_count = 0
        current_a_move_x = 0
        current_a_move_y = 0

        leftover_x_from_b_move = self.x_goal - current_b_move_count * self.b_button.x_move
        leftover_y_from_b_move = self.y_goal - current_b_move_count * self.b_button.y_move

        while current_b_move_count >= 0:
            while current_a_move_x <= leftover_x_from_b_move and current_a_move_y <= leftover_y_from_b_move:
                if current_a_move_x == leftover_x_from_b_move and current_a_move_y == leftover_y_from_b_move:
                    self.winning_moves.append(WinningMove(a_presses=current_a_move_count, b_presses=current_b_move_count))
                current_a_move_count += 1
                current_a_move_x += self.a_button.x_move
                current_a_move_y += self.a_button.y_move
            # ready for next round
            current_b_move_count -= 1
            leftover_x_from_b_move += self.b_button.x_move
            leftover_y_from_b_move += self.b_button.y_move


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        claw_machines = parse_claw_machines(self.input_loader.load_input_array("\n\n"))
        total_cost = 0
        for claw_machine in claw_machines:
            claw_machine.calculate_winning_moves()
            if claw_machine.cheapest_winning_move is not None:
                total_cost += claw_machine.cheapest_winning_move.price
        return total_cost

    def run_part_two(self):
        return "---"


def parse_claw_machines(raw_claw_machines: list[str]) -> list[ClawMachine]:
    claw_machines: list[ClawMachine] = []

    for raw_claw_machine in raw_claw_machines:
        raw_button_a, raw_button_b, raw_prize = raw_claw_machine.split("\n")
        raw_button_a_x, raw_button_a_y = raw_button_a.split("Button A: X+")[1].split(", Y+")
        raw_button_b_x, raw_button_b_y = raw_button_b.split("Button B: X+")[1].split(", Y+")
        raw_prize_x, raw_prize_y = raw_prize.split("Prize: X=")[1].split(", Y=")
        claw_machines.append(ClawMachine(
            a_button=Button(int(raw_button_a_x), int(raw_button_a_y)),
            b_button=Button(int(raw_button_b_x), int(raw_button_b_y)),
            x_goal=int(raw_prize_x),
            y_goal=int(raw_prize_y),
        ))

    return claw_machines
