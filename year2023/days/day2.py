from dataclasses import dataclass, field
from typing import Union

from helpers import InputLoader, regex_extract_multiple, regex_extract
from lib.abstract_day import AbstractDay
from lib.exceptions import RegexNotFoundException


GAME_LINE_REGEX = r"Game (\d+): (.*)"
GREEN_COUNT_REGEX = r"(\d+) green"
RED_COUNT_REGEX = r"(\d+) red"
BLUE_COUNT_REGEX = r"(\d+) blue"


@dataclass
class Draw:
    red: int = 0
    green: int = 0
    blue: int = 0


@dataclass
class Game:
    id: int
    draws: list[Draw] = field(default_factory=list)


def load_games(input_lines: list[str]) -> list[Game]:
    games = []
    for line in input_lines:
        games.append(load_game(line))
    return games


def load_game(line: str) -> Game:
    game_id, game_draws_string = regex_extract_multiple(GAME_LINE_REGEX, line, 2)
    game = Game(int(game_id))
    game.draws = extract_game_draws(game_draws_string)
    return game


def extract_game_draws(game_draws_string: str) -> list[Draw]:
    draws = []
    for game_draw_string in game_draws_string.split(";"):
        draws.append(extract_game_draw(game_draw_string))
    return draws


def extract_game_draw(game_draw_string: str) -> Draw:
    draw = Draw()

    try:
        draw.red = int(regex_extract(RED_COUNT_REGEX, game_draw_string))
    except RegexNotFoundException:
        pass  # no regex found - no balls were drawn, count stays at 0
    try:
        draw.green = int(regex_extract(GREEN_COUNT_REGEX, game_draw_string))
    except RegexNotFoundException:
        pass  # no regex found - no balls were drawn, count stays at 0
    try:
        draw.blue = int(regex_extract(BLUE_COUNT_REGEX, game_draw_string))
    except RegexNotFoundException:
        pass  # no regex found - no balls were drawn, count stays at 0

    return draw


class DayRunner(AbstractDay):

    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        draw_limit = Draw(red=12, green=13, blue=14)
        input_lines = self.input_loader.load_input_array(item_separator="\n")
        games = load_games(input_lines)
        result = part_one(games, draw_limit)
        return result

    def run_part_two(self):
        input_lines = self.input_loader.load_input_array(item_separator="\n")
        games = load_games(input_lines)
        result = part_two(games)
        return result


def part_one(games: list[Game], draw_limit: Draw) -> int:
    sum_of_possible_games = 0
    for game in games:
        if game_is_possible(game, draw_limit):
            sum_of_possible_games += game.id
    return sum_of_possible_games


def game_is_possible(game: Game, draw_limit: Draw) -> bool:
    for draw in game.draws:
        if not draw_is_possible(draw, draw_limit):
            return False
    return True


def draw_is_possible(draw: Draw, draw_limit: Draw) -> bool:
    return (draw.red <= draw_limit.red and
            draw.green <= draw_limit.green and
            draw.blue <= draw_limit.blue)


def part_two(games: list[Game]) -> int:
    sum_of_set_powers = 0
    for game in games:
        sum_of_set_powers += get_minimal_set_power(game)
    return sum_of_set_powers


def get_minimal_set_power(game: Game) -> int:
    minimal_set_needed = Draw()
    for draw in game.draws:
        if draw.red > minimal_set_needed.red:
            minimal_set_needed.red = draw.red
        if draw.green > minimal_set_needed.green:
            minimal_set_needed.green = draw.green
        if draw.blue > minimal_set_needed.blue:
            minimal_set_needed.blue = draw.blue
    return minimal_set_needed.red * minimal_set_needed.blue * minimal_set_needed.green
