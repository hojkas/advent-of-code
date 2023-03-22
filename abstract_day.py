from abc import ABC, abstractmethod


class AbstractDay(ABC):
    @abstractmethod
    def add_input_loader(self, input_loader):
        pass

    @abstractmethod
    def run_part_one(self):
        pass

    @abstractmethod
    def run_part_two(self):
        pass
