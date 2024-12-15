from enum import Enum


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)
    UP_RIGHT = (-1, 1)
    UP_LEFT = (-1, -1)
    DOWN_RIGHT = (1, 1)
    DOWN_LEFT = (1, -1)

    @property
    def opposite(self) -> 'Direction':
        return {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
            Direction.UP_RIGHT: Direction.DOWN_LEFT,
            Direction.UP_LEFT: Direction.DOWN_RIGHT,
            Direction.DOWN_RIGHT: Direction.UP_LEFT,
            Direction.DOWN_LEFT: Direction.UP_RIGHT,
        }[self]

    @property
    def next_clockwise_cardinal(self) -> 'Direction':
        return {
            Direction.UP: Direction.RIGHT,
            Direction.DOWN: Direction.LEFT,
            Direction.LEFT: Direction.UP,
            Direction.RIGHT: Direction.DOWN,
        }[self]

    @property
    def next_clockwise_omnidirectional(self) -> 'Direction':
        return {
            Direction.UP: Direction.UP_RIGHT,
            Direction.UP_RIGHT: Direction.RIGHT,
            Direction.RIGHT: Direction.DOWN_RIGHT,
            Direction.DOWN_RIGHT: Direction.DOWN,
            Direction.DOWN: Direction.DOWN_LEFT,
            Direction.DOWN_LEFT: Direction.LEFT,
            Direction.LEFT: Direction.UP_LEFT,
            Direction.UP_LEFT: Direction.UP,
        }[self]

    @property
    def next_counter_clockwise_cardinal(self) -> 'Direction':
        return {
            Direction.UP: Direction.LEFT,
            Direction.DOWN: Direction.RIGHT,
            Direction.LEFT: Direction.DOWN,
            Direction.RIGHT: Direction.UP,
        }[self]

    @property
    def next_counter_clockwise_omnidirectional(self) -> 'Direction':
        return {
            Direction.UP: Direction.UP_LEFT,
            Direction.UP_RIGHT: Direction.UP,
            Direction.RIGHT: Direction.UP_RIGHT,
            Direction.DOWN_RIGHT: Direction.RIGHT,
            Direction.DOWN: Direction.DOWN_RIGHT,
            Direction.DOWN_LEFT: Direction.DOWN,
            Direction.LEFT: Direction.DOWN_LEFT,
            Direction.UP_LEFT: Direction.LEFT,
        }[self]
