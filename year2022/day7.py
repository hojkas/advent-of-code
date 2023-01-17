import os
from abstract_day import AbstractDay
from exceptions import RunException
from helpers import CC
from input_loader import InputLoader
from abc import abstractmethod, ABC


def print_result(part, result):
    filename = os.path.basename(__file__).split('.')[0]
    print('[', filename, '] ', CC.GREEN, 'Result of part ', part, CC.NC, ': ', result, sep='')


class Item(ABC):
    @abstractmethod
    def size(self):
        pass

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def print_whole_structure(self):
        pass

    def is_dir(self):
        return isinstance(self, Directory)

    def is_file(self):
        return isinstance(self, File)


class Directory(Item):
    def __init__(self,  name, parent):
        self._name: str = name
        self._content_map: dict[str, Item] = {}
        self._size: int | None = None
        self._parent = parent

        self.depth = 0 if parent is None else parent.depth + 1

    def count_size(self):
        self._size = 0
        for item in self._content_map.values():
            self._size += item.size()

    def size(self):
        if self._size is None:
            self.count_size()
        return self._size

    def name(self):
        return self._name

    def add_item(self, item: Item):
        self._content_map[item.name()] = item

    def cd_parent(self):
        if self.is_root():
            raise RunException('Cant go up on root directory')
        return self._parent

    def cd_child(self, child_name):
        try:
            child = self._content_map[child_name]
            if child.is_dir():
                return child
            else:
                raise RunException('Cant cd into file')
        except KeyError:
            raise RunException('Child with name', child_name, 'doesnt exist in current dir ', self.name())

    def is_root(self):
        return self._parent is None

    def __str__(self):
        return "  " * self.depth + "- " + self.name() + " (dir)"

    def print_whole_structure(self):
        print(str(self))
        for item in self._content_map.values():
            item.print_whole_structure()

    def get_all_dir_children(self):
        children = []
        for child in self._content_map.values():
            if child.is_dir():
                children.append(child)
        return children

    def get_all_file_children(self):
        children = []
        for child in self._content_map.values():
            if child.is_file():
                children.append(child)
        return children

    def get_all_children(self):
        return self._content_map.values()


class File(Item):
    def __init__(self, name, size, parent):
        self._name = name
        self._size = int(size)
        self._parent = parent
        self.depth = parent.depth + 1

    def size(self):
        return self._size

    def name(self):
        return self._name

    def __str__(self):
        return "  " * self.depth + "- " + self.name() + " (file, size=" + str(self.size()) + ")"

    def print_whole_structure(self):
        print(str(self))


def construct_file_tree(input_array):
    root = Directory('/', None)
    current_dir = root
    doing_ls = False
    for line in input_array:
        split_command = line.split(' ')

        if split_command[0] == "$" and split_command[1] == "cd" and len(split_command) == 3:
            doing_ls = False
            if split_command[2] == "/":
                current_dir = root
            elif split_command[2] == "..":
                current_dir = current_dir.cd_parent()
            else:
                current_dir = current_dir.cd_child(split_command[2])
        elif split_command[0] == "$" and split_command[1] == "ls":
            doing_ls = True
        elif len(split_command) == 2 and doing_ls:
            if split_command[0] == "dir":
                new_dir = Directory(split_command[1], current_dir)
                current_dir.add_item(new_dir)
            else:
                new_file = File(split_command[1], split_command[0], current_dir)
                current_dir.add_item(new_file)
        else:
            raise RunException('Should not happen, is the command ok?' + line + split_command)
    return root


def part_one(file_tree: Directory):
    return part_one_sub_sum(file_tree)


def part_one_sub_sum(curr_dir: Directory):
    s = 0
    if curr_dir.size() <= 100000:
        s += curr_dir.size()
    child: Directory
    for child in curr_dir.get_all_dir_children():
        s += part_one_sub_sum(child)
    return s


def part_two(file_tree: Directory):
    capacity = 70000000  # 70 000 000
    total_space_needed = 30000000  # 30 000 000
    space_to_free = total_space_needed - capacity + file_tree.size()

    best_fit = part_two_sub_search(file_tree, None, space_to_free)
    return best_fit


def part_two_sub_search(curr_dir: Directory, best_fit_so_far: int | None, target: int) -> int:
    if best_fit_so_far is None:
        best_fit_so_far = curr_dir.size()
    elif target <= curr_dir.size() < best_fit_so_far:
        best_fit_so_far = curr_dir.size()
    child: Directory
    for child in curr_dir.get_all_dir_children():
        best_fit_so_far = part_two_sub_search(child, best_fit_so_far, target)
    return best_fit_so_far


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: InputLoader | None = None
        self.debug_mode = False

    def dbg(self, *args, **kwargs):
        if self.debug_mode:
            print(*args, **kwargs)

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def use_debug(self, use_debug=False):
        self.debug_mode = use_debug

    def run_part_one(self):
        command_array = self.input_loader.load_input_array('\n')
        file_tree = construct_file_tree(command_array)
        result = part_one(file_tree)
        print_result(1, result)

    def run_part_two(self):
        command_array = self.input_loader.load_input_array('\n')
        file_tree = construct_file_tree(command_array)
        result = part_two(file_tree)
        print_result(2, result)

