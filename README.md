# Player Code Updates

The provided player code was updated mainly in the following ways:

- Removed dependencies on `board.py`. `RandomPlayer` and `SimplePlayer` no longer import `EMPTY`, `SIZE`, or `simulate` from another file. The constants and required simulation logic are now included within the player files so that they can run independently.
- Changed the `Player` constructor from `Player(go_first)` to `Player(color)`, using `0` for black and `1` for white to match the project specification.
- Updated `RandomPlayer` and `SimplePlayer` to use `super().__init__(color)`.
- Updated `Player` to use Python's `ABC` and `@abstractmethod` for proper abstraction.
- Moved helper logic used by the players into their respective classes for consistency.
