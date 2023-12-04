from typing import Union
from dataclasses import dataclass, field

from lib.abstract_day import AbstractDay
from helpers import InputLoader, regex_extract


@dataclass
class Card:
    id: int
    winning_numbers: list[int] = field(default_factory=list)
    card_numbers: list[int] = field(default_factory=list)
    winning_matches: int = 0


@dataclass
class CardPile:
    card: Card
    count: int


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_list = self.input_loader.load_input_array(item_separator="\n")
        cards = load_cards(input_list)
        result = calculate_cards_winning_points(cards)
        return result

    def run_part_two(self):
        input_list = self.input_loader.load_input_array(item_separator="\n")
        cards = load_cards(input_list)
        card_piles = create_original_card_piles(cards)
        result = process_card_piles(card_piles)
        return result


def load_cards(input_list: list[str]) -> list[Card]:
    cards = []
    for line in input_list:
        cards.append(load_card(line))
    return cards


def load_card(line: str) -> Card:
    card_info_part, rest_of_line = line.split(":")
    winning_numbers_part, card_numbers_part = rest_of_line.split("|")

    card_id = int(regex_extract(r"Card +(\d+)", card_info_part))
    card = Card(id=card_id)

    for winning_number_string in winning_numbers_part.split(" "):
        if not winning_number_string:
            continue  # empty string is a result of more spaces or start/end of string
        card.winning_numbers.append(int(winning_number_string))

    for card_number_string in card_numbers_part.split(" "):
        if not card_number_string:
            continue
        card.card_numbers.append(int(card_number_string))

    current_matches = 0
    for card_number in card.card_numbers:
        if card_number in card.winning_numbers:
            current_matches += 1
    card.winning_matches = current_matches

    return card


def calculate_cards_winning_points(cards: list[Card]) -> int:
    total = 0
    for card in cards:
        total += calculate_card_winning_points(card)
    return total


def calculate_card_winning_points(card: Card) -> int:
    if card.winning_matches == 0:
        return 0
    else:
        return 2 ** (card.winning_matches - 1)


def create_original_card_piles(cards: list[Card]) -> dict[int, CardPile]:
    card_piles = {}
    for card in cards:
        card_piles[card.id] = CardPile(card, 1)
    return card_piles


def process_card_piles(card_piles: dict[int, CardPile]):
    card_id_order = list(card_piles.keys())
    card_id_order.sort()

    for card_id in card_id_order:
        process_card_pile(card_id, card_piles)

    return sum(card_pile.count for card_pile in card_piles.values())


def process_card_pile(card_id: int, card_piles: dict[int, CardPile]) -> None:
    for i in range(card_piles[card_id].card.winning_matches):
        won_card_id = card_id + i + 1
        card_piles[won_card_id].count += card_piles[card_id].count
