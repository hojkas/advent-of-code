from typing import Optional
from dataclasses import dataclass, field
from enum import Enum

from lib.abstract_day import AbstractDay
from helpers import InputLoader


class WinType(Enum):
    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIR = 2
    THREE_OF_KIND = 3
    FULL_HOUSE = 4
    FOUR_OF_KIND = 5
    FIVE_OF_KIND = 6


@dataclass
class Card:
    representation: str
    value: int

    def __init__(self, representation: str, playing_with_jokers: bool = False):
        self.representation = representation
        if representation == "A":
            self.value = 14
        elif representation == "K":
            self.value = 13
        elif representation == "Q":
            self.value = 12
        elif representation == "J":
            if playing_with_jokers:
                self.value = 1
            else:
                self.value = 11
        elif representation == "T":
            self.value = 10
        else:
            self.value = int(representation)


@dataclass
class CardHand:
    bid: int
    cards: list[Card]
    win_type: Optional[WinType] = None
    win_type_value: Optional[int] = None
    rank: Optional[int] = None


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_lines = self.input_loader.load_input_array(item_separator="\n")
        card_hands = load_card_hands(input_lines)
        assign_win_type_to_cards(card_hands)
        card_hands.sort(key=(lambda x: x.win_type_value))
        assign_ranks(card_hands)
        result = calculate_total_winnings(card_hands)
        return result

    def run_part_two(self):
        input_lines = self.input_loader.load_input_array(item_separator="\n")
        card_hands = load_card_hands(input_lines, with_jokers=True)
        assign_win_type_to_cards(card_hands)
        card_hands.sort(key=(lambda x: x.win_type_value))
        assign_ranks(card_hands)
        result = calculate_total_winnings(card_hands)
        return result


def load_card_hands(input_lines: list[str], with_jokers: bool = False) -> list[CardHand]:
    cards = []
    for line in input_lines:
        cards.append(load_card_hand(line, with_jokers))
    return cards


def load_card_hand(line: str, with_jokers: bool) -> CardHand:
    card_values, card_bid = line.split(" ")
    cards = [Card(x, with_jokers) for x in card_values]
    return CardHand(
        cards=cards,
        bid=int(card_bid)
    )


def assign_win_type_to_cards(card_hands: list[CardHand]) -> None:
    for card_hand in card_hands:
        card_hand.win_type = find_win_type_for_card(card_hand)
        card_hand.win_type_value = calculate_win_type_value(card_hand)


def find_win_type_for_card(card_hand: CardHand) -> WinType:
    card_types = {}
    for card in card_hand.cards:
        if card.value in card_types.keys():
            card_types[card.value] += 1
        else:
            card_types[card.value] = 1
    if 1 not in card_types.keys():  # no joker present
        return find_win_type_without_jokers(card_types)
    best_win_type_so_far = WinType.HIGH_CARD
    for non_joker_value in [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14]:
        if non_joker_value not in card_types.keys():
            if card_types[1] == 5:
                return WinType.FIVE_OF_KIND  # all jokers
            continue  # no need to try replacing those as that will always be worse
        new_card_types = {key: value for key, value in card_types.items() if key != 1}
        new_card_types[non_joker_value] += card_types[1]  # pretend the jokers are this card type
        new_win_type = find_win_type_without_jokers(new_card_types)
        if new_win_type.value > best_win_type_so_far.value:
            best_win_type_so_far = new_win_type
    return best_win_type_so_far


def find_win_type_without_jokers(card_types: dict[int, int]) -> WinType:
    card_type_counts = [val for val in card_types.values()]
    card_type_counts.sort(reverse=True)
    if card_type_counts[0] == 5:
        return WinType.FIVE_OF_KIND
    if card_type_counts[0] == 4:
        return WinType.FOUR_OF_KIND
    if card_type_counts[0] == 3:
        if card_type_counts[1] == 2:
            return WinType.FULL_HOUSE
        else:
            return WinType.THREE_OF_KIND
    if card_type_counts[0] == 2:
        if card_type_counts[1] == 2:
            return WinType.TWO_PAIR
        else:
            return WinType.ONE_PAIR
    return WinType.HIGH_CARD


def calculate_win_type_value(card_hand: CardHand) -> int:
    return (
            (card_hand.cards[4].value - 1)
            + (card_hand.cards[3].value - 1) * 14
            + (card_hand.cards[2].value - 1) * 14 * 14
            + (card_hand.cards[1].value - 1) * (14 ** 3)
            + (card_hand.cards[0].value - 1) * (14 ** 4)
            + int(card_hand.win_type.value) * (14 ** 5)
    )


def assign_ranks(sorted_card_hands: list[CardHand]) -> None:
    for i, card_hand in enumerate(sorted_card_hands):
        card_hand.rank = i + 1


def calculate_total_winnings(card_hands: list[CardHand]) -> int:
    winnings = 0
    for card_hand in card_hands:
        winnings += card_hand.rank * card_hand.bid
    return winnings
