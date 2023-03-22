import os
from typing import Union
from abstract_day import AbstractDay
from exceptions import RunException
from old_helpers import CC
from input_loader import InputLoader


def print_result(part, result):
    filename = os.path.basename(__file__).split('.')[0]
    print('[', filename, '] ', CC.GREEN, 'Result of part ', part, CC.NC, ': ', result, sep='')


class Tree:
    def __init__(self, height):
        self.height = int(height)
        self.visible = False
        self.scenic_score = 1


class Forest:
    def __init__(self, input_array: list[str]):
        self.forest = [[Tree(x) for x in y] for y in input_array]
        self.width = len(self.forest[0])
        self.height = len(self.forest)
        self.visible_trees = 0

    def _calculate_row_visiblity(self, tree_list):
        max_tree = -1
        for tree in tree_list:
            if tree.height <= max_tree:
                continue

            if not tree.visible:
                self.visible_trees += 1
            tree.visible = True
            max_tree = tree.height

    def calculate_visibility(self):
        for line in self.forest:
            self._calculate_row_visiblity(line)
            self._calculate_row_visiblity(line[::-1])

        for i in range(self.width):
            column = [line[i] for line in self.forest]
            self._calculate_row_visiblity(column)
            self._calculate_row_visiblity(column[::-1])

    def _calculate_tree_scenic_score_in_direction(self, tree_row, tree_col, row_diff, col_diff):
        visual_range = 0
        curr_row = tree_row + row_diff
        curr_col = tree_col + col_diff
        tree = self.forest[tree_row][tree_col]

        while True:
            if curr_col == -1 or curr_row == -1 or curr_row == self.height or curr_col == self.width:
                break
            visual_range += 1
            if self.forest[curr_row][curr_col].height >= tree.height:
                break
            curr_row += row_diff
            curr_col += col_diff

        tree.scenic_score *= visual_range

    def _calculate_tree_scenic_score(self, row, col):
        if row == 0 or col == 0 or row + 1 == self.height or col + 1 == self.width:
            self.forest[row][col].scenic_score = 0
            return

        self._calculate_tree_scenic_score_in_direction(row, col, 1, 0)
        self._calculate_tree_scenic_score_in_direction(row, col, -1, 0)
        self._calculate_tree_scenic_score_in_direction(row, col, 0, 1)
        self._calculate_tree_scenic_score_in_direction(row, col, 0, -1)

    def calculate_scenic_scores(self):
        for row in range(self.height):
            for col in range(self.width):
                self._calculate_tree_scenic_score(row, col)

    def get_best_scenic_score(self):
        best_scenic_score = -1
        for line in self.forest:
            for tree in line:
                if tree.scenic_score > best_scenic_score:
                    best_scenic_score = tree.scenic_score
        return best_scenic_score

    def print_forest(self, only_visible=False):
        for line in self.forest:
            for tree in line:
                if only_visible and not tree.visible:
                    print(" ", end="")
                else:
                    print(tree.height, end="")
            print()


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        forest = Forest(self.input_loader.load_input_array(item_separator="\n"))
        forest.calculate_visibility()
        result = forest.visible_trees
        print_result(1, result)

    def run_part_two(self):
        forest = Forest(self.input_loader.load_input_array(item_separator="\n"))
        forest.calculate_scenic_scores()
        result = forest.get_best_scenic_score()
        print_result(2, result)
