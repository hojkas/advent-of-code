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

    def get_before_rules_filtered(self, page_filter: list[int]) -> dict[int, list[int]]:
        before_rules = {}
        for item in self.items:
            if item.before_page not in page_filter or item.after_page not in page_filter:
                continue

            if item.before_page not in before_rules:
                before_rules[item.before_page] = [item.after_page]
            else:
                before_rules[item.before_page].append(item.after_page)
        return before_rules

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

    def create_correct_order(self, page_ordering: PageOrdering) -> None:
        applicable_rules = page_ordering.get_before_rules_filtered(self.pages)
        ordered = []
        unordered = self.pages

        while len(unordered) > 0:
            removed_one = False
            for page_number in unordered:
                if page_number not in applicable_rules:  # not a key - is not in relationship with any other page to be before it
                    ordered.append(page_number)
                    unordered.remove(page_number)
                    self._cleanse_applicable_rules(page_number, applicable_rules)
                    removed_one = True
                    continue
            if not removed_one:
                raise RuntimeError("No key was removed. Cyclic dependency detected.")

        self.pages = ordered

    @staticmethod
    def _cleanse_applicable_rules(removed_number: int, applicable_rules: dict[int, list[int]]) -> None:
        # remove the dependancy
        for after_pages in applicable_rules.values():
            if removed_number in after_pages:
                after_pages.remove(removed_number)
        # remove empty entries
        keys_to_pop = []
        for key, value in applicable_rules.items():
            if len(value) == 0:
                keys_to_pop.append(key)
        for key in keys_to_pop:
            applicable_rules.pop(key)


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
        page_ordering_raw, page_sets_raw = self.input_loader.load_input_array_of_array(
            subarray_separator="\n\n", item_separator="\n"
        )
        page_ordering = convert_page_ordering(page_ordering_raw)
        page_sets = convert_page_sets(page_sets_raw)
        wrongly_ordered_page_sets = [page_set for page_set in page_sets if not page_set.is_valid(page_ordering)]
        middle_page_sum = 0
        for page_set in wrongly_ordered_page_sets:
            page_set.create_correct_order(page_ordering)
            middle_page_sum += page_set.middle_page
        return middle_page_sum


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

