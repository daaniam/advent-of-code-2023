def load_file() -> list[str]:
    # Load file from disk
    with open("input.txt", "rb") as f:
        lines = f.readlines()
        return [line.decode("utf-8").strip() for line in lines]


input_elf_document = load_file()


def is_int(char: str) -> bool:
    try:
        int(char)
        return True
    except ValueError:
        return False


word_num_map = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
}

input_example_from_web = [
    "two1nine",
    "eightwothree",
    "abcone2threexyz",
    "xtwone3four",
    "4nineeightseven2",
    "zoneight234",
    "7pqrstsixteen",
]


input_anything = [
    "abc123sevenineight4569ee",
    "4twozgxqjbdsone963two",
    "nineeight6khkrgsdcfpkcjkglbq5lxkjxsvrrktmfzsbz",
    "onetwothreefourfivesixseveneightnineten",
]


def first_int_from_left(composed: str) -> str:
    for char in composed:
        if is_int(char):
            return char


def first_int_from_right(composed: str) -> str:
    for char in reversed(composed):
        if is_int(char):
            return char


def combine_left_right(composed: str):
    left = first_int_from_left(composed)
    right = first_int_from_right(composed)
    combined = int(str(left) + str(right))
    return combined


def find_occurrence(line: str, word: str, start_index: int):
    """Find an occurrence of a given word starting from the given index from the left

    Example: abc123sevenineight4569ee = word "seven" starts at index 6
    """
    # print(f"Looking for {word} in {line} starting index {start_index}")
    found_index = line.find(word, start_index)
    return found_index


def localize_words(messed: str):
    """
    Iterate over word:num map and find index of the first letter for each word.
    If the word is if found, set last_index to it's first letter index to avoid finding it again.
    Iterate until there is no index found = no more word from word:num mapping present.

    Return dict with location of all WORDS

    Exmaple:
      abc123sevenineight4569ee = {6: 7, 13: 8, 10: 9}
        > "seven" on index 6
        > "eight" on index 13
        > "nine" on index 10
    """
    word_locations: dict[int, int] = {}

    for word, num in word_num_map.items():
        last_index_found = -1
        found_index = find_occurrence(messed, word, start_index=last_index_found + 1)
        # ...until found
        while found_index > -1:
            word_locations.update({found_index: num})
            last_index_found = found_index
            found_index = find_occurrence(
                messed, word, start_index=last_index_found + 1
            )

    return word_locations


def compose(line: str, localized: dict[int, int]):
    """
    Compose new string with inplace injection of NUM before WORD

    Example;
      abc123sevenineight4569ee = {6: 7, 13: 8, 10: 9}
        > "seven" on index 6
        > "eight" on index 13
        > "nine" on index 10

    Composed new string: abc1237seve9nin8eight4569ee
    """
    composed = []
    for char_index, char in enumerate(line):
        if char_index in localized.keys():
            composed.append(str(localized[char_index]))

        composed.append(str(char))

    return composed


"""
Run above methods in order.
- Localize every occurrence of WORD number representation in messed lines.
- compose new string with NUM injection
- combine first NUM and last NUM
- SUM values
"""
sum_all = []
for i, line in enumerate(input_elf_document):
    print(i, " - ", line)

    localized: dict[int:str] = localize_words(line)
    print("localized (index:number):", localized)
    composed = compose(line=line, localized=localized)
    composed_string = "".join(composed)
    print("composed", composed_string)
    combined_left_right = combine_left_right(composed_string)
    print("combined_left_right", combined_left_right)
    sum_all.append(int(combined_left_right))
    print("-----")

print(sum(sum_all))
