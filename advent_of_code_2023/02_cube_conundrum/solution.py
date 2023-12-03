"""
Part 1: 2720
Part 2: 71535
"""

from typing import Literal, Self
import re
from functools import reduce
from operator import mul


CubeColorT = Literal["red", "green", "blue"]


def load_file() -> list[str]:
    # Load file from disk
    with open("input.txt", "rb") as f:
        lines = f.readlines()
        return [line.decode("utf-8").strip() for line in lines]


input_all_games = load_file()

input_web_example = [
    "Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green",
    "Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue",
    "Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red",
    "Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red",
    "Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green",
]


class ReprMixin:
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"


class Cube(ReprMixin):
    def __init__(self, color: CubeColorT):
        self.color = color


class GameSet(ReprMixin):
    def __init__(self, revealed_order: int):
        self.revealed_order = revealed_order
        self.cubes: list[Cube] = []

    def add_cube(self, cube: Cube) -> None:
        self.cubes.append(cube)

    def extend_cubes(self, cubes: list[Cube]):
        self.cubes.extend(cubes)

    def cubes(self, color: CubeColorT) -> list[Cube]:
        return [cube for cube in self.cubes if cube.color == color]

    def cubes_sum(self, color: CubeColorT) -> int:
        return len([cube for cube in self.cubes if cube.color == color])


class CubeGame(ReprMixin):
    def __init__(self, game_number: int):
        self.game_number = game_number
        self.game_sets: list[GameSet] = []

    def __eq__(self, other: Self):
        return self.game_number == other.game_number

    def __hash__(self):
        return hash(self.game_number)

    def add_set(self, game_set: GameSet) -> None:
        self.game_sets.append(game_set)

    def revealed_cubes(self, color: CubeColorT):
        """Revealed Cubes by color for the entire game - in every GameSet"""
        return [game_set.cubes(color=color) for game_set in self.game_sets]

    def minimum_cubes_per_color(self, colors: list[CubeColorT]):
        """
        - Find the highest value for every color in every set

        """
        result = {}
        for color in colors:
            highest_value = -1
            for game_set in self.game_sets:
                cubes_of_same_color_count = game_set.cubes_sum(color=color)
                if cubes_of_same_color_count > highest_value:
                    highest_value = cubes_of_same_color_count

            result.setdefault(color, highest_value)

        return result


def game_factory(game_record: str) -> CubeGame:
    # print("game_record", game_record)
    right_game, left_sets = re.split(":", game_record)

    game_number = re.sub("Game", "", right_game).strip()
    # print("game_number", game_number)
    new_game = CubeGame(game_number=int(game_number))

    game_set_list = list(map(lambda item: item.strip(), re.split(";", left_sets)))
    # print("game_set_list", game_set_list)

    for set_index, game_set in enumerate(game_set_list):
        new_set = GameSet(revealed_order=set_index)
        new_game.add_set(game_set=new_set)
        cube_list = list(map(lambda item: item.strip(), re.split(",", game_set)))
        # print("cube_list", cube_list)
        for cube in cube_list:
            # print("cube", cube)
            cubes_count, cube_color = re.split(" ", cube)
            # print("cubes_count", cubes_count, "cube_color", cube_color)
            new_cubes = [Cube(color=cube_color) for _ in range(int(cubes_count))]
            # print("new_cubes", new_cubes)
            new_set.extend_cubes(cubes=new_cubes)

    return new_game


def normalized_games(game_records: list[str]):
    return [game_factory(game_record=game_record) for game_record in game_records]


game_list_all = normalized_games(input_all_games)
game_list_web_example = normalized_games(input_web_example)


# Find impossible games according to rules - restricted number of cubes in one set.
def resolve_impossible_game(game: CubeGame, for_color: CubeColorT, max_in_bag: int) -> bool:
    """Returns True if the game is impossible"""
    # print(game.game_number)

    # Get SUM of colors for every set in the game
    for game_set in game.game_sets:
        cubes_in_set_with_same_color = game_set.cubes_sum(color=for_color)

        # If there is more colors revealed in one set then in the entire bag, the game is not possible
        if cubes_in_set_with_same_color > max_in_bag:
            print(
                f"Game ID {game.game_number} is impossible for color {for_color} with maximum {max_in_bag} cubes in the "
                f"bag compared to {cubes_in_set_with_same_color} revealed in set {game_set.revealed_order}"
            )
            return True

    return False


def find_impossible_games(rules: dict[CubeColorT, int]):
    impossible_games = []

    for game in game_list_all:
        for color, max_in_bag in rules.items():
            is_impossible = resolve_impossible_game(game=game, for_color=color, max_in_bag=max_in_bag)
            if is_impossible and game not in impossible_games:
                impossible_games.append(game)
                break

    possible_games = set(game_list_all) - set(impossible_games)

    return possible_games, impossible_games


if __name__ == "__main__":
    part_one = True
    part_two = True

    # Part 1: Find impossible games
    if part_one:
        print("PART ONE")
        rules: dict[CubeColorT, int] = {"red": 12, "green": 13, "blue": 14}
        possible_games, impossible_games = find_impossible_games(rules)

        print("Impossible sum:", len(impossible_games))
        print("Possible sum:", len(possible_games))
        checksum = len(impossible_games) + len(possible_games)
        if checksum > len(input_all_games):
            raise ValueError(f"Checksum value {checksum} can't be higher the list of all games {len(input_all_games)} ")
        print("Checksum:", checksum)

        possible_ids = [game.game_number for game in possible_games]
        print("Happy number", sum(possible_ids))

    # Part 2: Find minimum cubes in the bag
    if part_two:
        print("\nPART TWO")
        multiply_results = []
        colors = ["red", "green", "blue"]
        for game in game_list_all:
            minimum_cubes_per_color = game.minimum_cubes_per_color(colors=colors)
            cube_set_multiplied = reduce(mul, minimum_cubes_per_color.values())  # Multiply numbers together
            multiply_results.append(cube_set_multiplied)
            print(
                "Game ID",
                game.game_number,
                "has minimum set of cubes:",
                minimum_cubes_per_color,
                "with multiply result:",
                cube_set_multiplied,
            )

        print("Happy number:", sum(multiply_results))
