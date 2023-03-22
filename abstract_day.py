from abc import ABC, abstractmethod
from typing import Any


class AbstractDay(ABC):
    @abstractmethod
    def add_input_loader(self, input_loader) -> None:
        pass

    @abstractmethod
    def run_part_one(self) -> Any:
        pass

    @abstractmethod
    def run_part_two(self) -> Any:
        pass
