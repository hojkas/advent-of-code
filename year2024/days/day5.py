from dataclasses import dataclass, field
from typing import Optional

from lib.abstract_day import AbstractDay
from helpers import InputLoader


@dataclass
class PageOrderItem:
    before_page: int
    after_page: int


@dataclass
class PageOrdering:
    items: list[PageOrderItem] = field(default_factory=list)
    before_pages: dict[int, list[PageOrderItem]] = field(default_factory=dict)
    after_pages: dict[int, list[PageOrderItem]] = field(default_factory=dict)

    def create_bindings(self):
        self.before_pages = {}
        self.after_pages = {}

        for item in self.items:
            if item.before_page not in self.before_pages:
                self.before_pages[item.before_page] = [item]
            else:
                self.before_pages[item.before_page].append(item)

            if item.after_page not in self.after_pages:
                self.after_pages[item.after_page] = [item]
            else:
                self.after_pages[item.after_page].append(item)

    def get_where_page_is_before(self, page_number: int) -> list[PageOrderItem]:
        return self.before_pages.get(page_number, [])

    def get_where_page_is_after(self, page_number: int) -> list[PageOrderItem]:
        return self.after_pages.get(page_number, [])

    def rule_exists(self, before_page: int, after_page: int) -> bool:
        before_rules = self.get_where_page_is_before(before_page)
        for rule in before_rules:
            if rule.after_page == after_page:
                return True
        return False


@dataclass
class PageSetItem:
    pages: list[int] = field(default_factory=list)

    @property
    def middle_page(self) -> int:
        return self.pages[len(self.pages) // 2]

    def is_valid(self, page_ordering: PageOrdering) -> bool:
        for first_item_index, first_item in enumerate(self.pages):
            for second_item_index in range(first_item_index + 1, len(self.pages)):
                second_item = self.pages[second_item_index]
                if page_ordering.rule_exists(before_page=second_item, after_page=first_item):
                    return False
        return True


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        page_ordering_raw, page_sets_raw = self.input_loader.load_input_array_of_array(
            subarray_separator="\n\n", item_separator="\n"
        )
        page_ordering = convert_page_ordering(page_ordering_raw)
        page_sets = convert_page_sets(page_sets_raw)
        result = sum(page_set.middle_page for page_set in page_sets if page_set.is_valid(page_ordering))
        return result

    def run_part_two(self):
        return "---"


def convert_page_ordering(page_ordering_raw: list[str]) -> PageOrdering:
    page_ordering = PageOrdering()
    for item_raw in page_ordering_raw:
        before_item, after_item = item_raw.split("|")
        page_ordering.items.append(PageOrderItem(int(before_item), int(after_item)))
    page_ordering.create_bindings()
    return page_ordering


def convert_page_sets(page_sets_raw: list[str]) -> list[PageSetItem]:
    page_sets = []
    for item_raw in page_sets_raw:
        item = PageSetItem()
        for number_string in item_raw.split(","):
            item.pages.append(int(number_string))
        page_sets.append(item)
    return page_sets

