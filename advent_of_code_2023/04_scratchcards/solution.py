"""
Part One: 15205
Part Two: 6189740
"""

import re
from enum import StrEnum
from typing import Self


def load_file() -> list[str]:
    with open("input.txt", "rb") as f:
        lines = f.readlines()
        return [line.decode("utf-8").strip() for line in lines]


input_deck = load_file()

input_web_example = [
    "Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53",
    "Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19",
    "Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1",
    "Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83",
    "Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36",
    "Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11",
]


class CardType(StrEnum):
    original = "original"
    cope = "copy"


class ScratchCard:
    def __init__(self, card_id: int, card_numbers: list[int], my_numbers: list[int], card_type: CardType):
        self.card_id = card_id
        self.card_numbers = card_numbers
        self.my_numbers = my_numbers
        self.type = card_type

    def __repr__(self):
        return f"Card({self.card_id})"  # , winning_nums: {self.winning_nums_count()})"  # card_nums: {self.card_numbers} my_nums: {self.my_numbers})"

    def __lt__(self, other: Self):
        return self.card_id < other.card_id

    def winning_nums(self) -> list[int]:
        return [n for n in self.my_numbers if n in self.card_numbers]

    def winning_nums_count(self) -> int:
        return len(self.winning_nums())

    def worth(self) -> int:
        if self.winning_nums():
            worth = 2
            return pow(worth, len(self.winning_nums()) - 1)
        return 0


class CardDeck:
    def __init__(self):
        self.cards: list[ScratchCard] = []

    def add_card(self, card: ScratchCard) -> None:
        self.cards.append(card)

    def deck_worth(self) -> int:
        return sum([card.worth() for card in self.cards])

    def get_following_cards(self, current_card: int, num_of_following_cards: int) -> list[ScratchCard]:
        return self.cards[current_card : current_card + num_of_following_cards]

    def get_cards(self, card_ids: list[int]) -> list[ScratchCard]:
        return [card for card in self.cards if card.card_id in card_ids]


class TheGame:
    def __init__(self, card_deck: CardDeck):
        self.deck: CardDeck = card_deck
        self.copies: list[ScratchCard] = []

    def num_of_copies(self, card_id: int) -> int:
        return len([card for card in self.copies if card.card_id == card_id])

    def all_cards(self) -> list[ScratchCard]:
        return sorted(self.deck.cards + self.copies)

    def card_instances(self, card_id: int) -> int:
        return len(
            [card for card in self.deck.cards if card.card_id == card_id]
            + [card for card in self.copies if card.card_id == card_id]
        )

    def instances_sum(self) -> int:
        """Return SUM of all instances for every card in the deck!

        In the original deck. Not All cards (copies included) in TheGame.
        """
        every_card_instance = []
        for card in self.deck.cards:
            every_card_instance.append(self.card_instances(card.card_id))
        return sum(every_card_instance)


def card_factory(row: str) -> ScratchCard:
    card_left, card_right = re.split(":", row)
    card_id = card_left.split()[1].strip()

    card_nums, my_nums = "".join(card_right).split("|")
    card_nums = [int(n.strip()) for n in re.split(" ", card_nums) if n]
    my_nums = [int(n.strip()) for n in re.split(" ", my_nums) if n]

    return ScratchCard(card_id=int(card_id), card_numbers=card_nums, my_numbers=my_nums, card_type=CardType.original)


def play_the_game(the_game: TheGame):
    for card in the_game.deck.cards:
        copies_won = []
        print(
            ">",
            card,
            f"- wins: {card.winning_nums_count()}",
            "- copies:",
            the_game.num_of_copies(card_id=card.card_id),
            "- instances:",
            the_game.card_instances(card_id=card.card_id),
        )
        winning_numbers_count = card.winning_nums_count()
        winning_copies = the_game.deck.get_following_cards(
            current_card=card.card_id, num_of_following_cards=winning_numbers_count
        )
        copies_won.extend(winning_copies)

        for card_copy in the_game.copies:
            if card_copy.card_id == card.card_id:
                copies_won.extend(winning_copies)

        the_game.copies.extend(copies_won)


if __name__ == "__main__":
    card_deck = CardDeck()
    for row in input_deck:
        card_deck.add_card(card=card_factory(row))

    the_game = TheGame(card_deck=card_deck)
    play_the_game(the_game=the_game)

    print("Happy number 1:", card_deck.deck_worth())
    print("Happy number 2:", the_game.instances_sum())
