from enum import Enum
from typing import Union

from abstract_day import AbstractDay
from exceptions import RunException
from input_loader import InputLoader


class GameSymbol(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3


class RoundResult(Enum):
    DEFEAT = 1,
    DRAW = 2,
    WIN = 3


def points_for_symbol(symbol):
    if symbol == GameSymbol.ROCK:
        return 1
    if symbol == GameSymbol.PAPER:
        return 2
    if symbol == GameSymbol.SCISSORS:
        return 3
    raise RunException('Given parameter is not valid symbol')


def evaluate_round_result(player_symbol, opponent_symbol):
    if not isinstance(player_symbol, GameSymbol) or not isinstance(opponent_symbol, GameSymbol):
        raise RunException('One of given parameteres are not valid symbol')

    if player_symbol == opponent_symbol:
        return RoundResult.DRAW

    if player_symbol == GameSymbol.ROCK:
        if opponent_symbol == GameSymbol.PAPER:
            return RoundResult.DEFEAT
        if opponent_symbol == GameSymbol.SCISSORS:
            return RoundResult.WIN

    if player_symbol == GameSymbol.SCISSORS:
        if opponent_symbol == GameSymbol.PAPER:
            return RoundResult.WIN
        if opponent_symbol == GameSymbol.ROCK:
            return RoundResult.DEFEAT

    if player_symbol == GameSymbol.PAPER:
        if opponent_symbol == GameSymbol.SCISSORS:
            return RoundResult.DEFEAT
        if opponent_symbol == GameSymbol.ROCK:
            return RoundResult.WIN

    raise RunException('This point should not be ever reached')


def get_symbol_for_result(opponent_symbol: GameSymbol, wanted_result: RoundResult) -> GameSymbol:
    if wanted_result == RoundResult.DRAW:
        return opponent_symbol

    if opponent_symbol == GameSymbol.ROCK:
        if wanted_result == RoundResult.WIN:
            return GameSymbol.PAPER
        if wanted_result == RoundResult.DEFEAT:
            return GameSymbol.SCISSORS

    if opponent_symbol == GameSymbol.SCISSORS:
        if wanted_result == RoundResult.WIN:
            return GameSymbol.ROCK
        if wanted_result == RoundResult.DEFEAT:
            return GameSymbol.PAPER

    if opponent_symbol == GameSymbol.PAPER:
        if wanted_result == RoundResult.WIN:
            return GameSymbol.SCISSORS
        if wanted_result == RoundResult.DEFEAT:
            return GameSymbol.ROCK

    raise RunException('This point should not be ever reached')


def points_for_round(player_symbol, opponent_symbol):
    res = points_for_symbol(player_symbol)
    round_result = evaluate_round_result(player_symbol, opponent_symbol)
    if round_result == RoundResult.WIN:
        res += 6
    if round_result == RoundResult.DRAW:
        res += 3
    return res


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None
        self.debug_mode = False

        self.abc = {
            'A': GameSymbol.ROCK,
            'B': GameSymbol.PAPER,
            'C': GameSymbol.SCISSORS
        }

        self.xyz = {
            'X': GameSymbol.ROCK,
            'Y': GameSymbol.PAPER,
            'Z': GameSymbol.SCISSORS
        }

        self.alt_xyz = {
            'X': RoundResult.DEFEAT,
            'Y': RoundResult.DRAW,
            'Z': RoundResult.WIN
        }

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_array = self.input_loader.load_input_array(item_separator='\n')
        result = self._part_one(input_array)
        return result

    def run_part_two(self):
        input_array = self.input_loader.load_input_array(item_separator='\n')
        result = self._part_two(input_array)
        return result

    def _part_one(self, input_array):
        tournament_points = 0
        for one_round in input_array:
            abc, xyz = one_round.split(' ')
            opponent = self.abc[abc]
            player = self.xyz[xyz]
            tournament_points += points_for_round(player, opponent)

        return tournament_points

    def _part_two(self, input_array):
        tournament_points = 0
        for one_round in input_array:
            abc, xyz = one_round.split(' ')
            opponent = self.abc[abc]
            wanted_result = self.alt_xyz[xyz]

            player = get_symbol_for_result(opponent, wanted_result)
            tournament_points += points_for_round(player, opponent)

        return tournament_points
