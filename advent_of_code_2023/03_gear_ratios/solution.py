"""
Part One: 549908

"""

from __future__ import annotations

from enum import StrEnum
from typing import Self, Any
from functools import reduce
from operator import mul

MappedEngineT = list[list["Node"]]


def load_file() -> list[str]:
    # Load file from disk
    with open("input.txt", "rb") as f:
        lines = f.readlines()
        return [line.decode("utf-8").strip() for line in lines]


input_engine = load_file()

input_web_example = [
    "467..114..",
    "...*......",
    "..35..633.",
    "......#...",
    "617*......",
    ".....+.58.",
    "..592.....",
    "......755.",
    "...$.*....",
    ".664.598..",
]


def is_int(val: Any):
    if val is None:
        return False

    try:
        int(val)
        return True
    except ValueError:
        return False


def localize_node(mapped_engine: MappedEngineT, row_number: int, index: int) -> Node:
    return mapped_engine[row_number][index]


class NodeTypeEnum(StrEnum):
    num = "num"
    symbol = "symbol"
    dot = "dot"

    def __repr__(self):
        return self.value


class NodePosition:
    def __init__(self, row_number: int, start_index: int, end_index: int):
        self.row_number = row_number
        self.start_index = start_index
        self.end_index = end_index

    def __repr__(self):
        return f"Position(r:{self.row_number} s:{self.start_index} e:{self.end_index})"


class Node:
    def __init__(self, value: int, node_type: NodeTypeEnum, position: NodePosition):
        self.type = node_type
        self.value = value
        self.position = position
        self.mapping: MappedEngineT | None = None

    def __repr__(self):
        return f"Node({self.type}, {self.value}, {self.position})"

    def __hash__(self):
        return hash(self.position)

    def is_size_one(self) -> bool:
        """Node holds only one position = its size = 1"""
        return self.position.start_index == self.position.end_index

    def is_left_edge(self) -> bool:
        left_index = self.position.start_index - 1

        # Edge Node - no one on left
        if left_index < 0:
            return True

        return False

    def is_right_edge(self) -> bool:
        if self.node_on_right() is None:
            return True

        return False

    def is_top_edge(self) -> bool:
        row_above = self.position.row_number - 1

        # Edge Node - no one above
        if row_above < 0:
            return True

        return False

    def is_bottom_edge(self) -> bool:
        row_below = self.position.row_number + 1

        try:
            self.mapping[row_below]
            return False
        except IndexError:
            return True

    def node_on_left(self) -> Self | None:
        """
        Coverage (1):
             - - - - - - - - - -
             - - 1 n o d e - - -
             - - - - - - - - - -
        """
        if not self.is_left_edge():
            left_index = self.position.start_index - 1
            return localize_node(mapped_engine=self.mapping, row_number=self.position.row_number, index=left_index)

        return None

    def node_on_right(self) -> Self | None:
        """
        Coverage (1):
             - - - - - - - - - -
             - - - n o d e 1 - -
             - - - - - - - - - -
        """

        try:
            right_index = self.position.end_index + 1
            return localize_node(mapped_engine=self.mapping, row_number=self.position.row_number, index=right_index)
        except IndexError:
            # Edge Node - no one on right
            return None

    def nodes_above(self) -> list[Self] | None:
        """
        Coverage (1):
             - - 1 1 1 1 1 1 - -
             - - - n o d e - - -
             - - - - - - - - - -
        """
        if not self.is_top_edge():
            row_above = self.position.row_number - 1
        else:
            return None

        if not self.is_left_edge():
            start_index = self.position.start_index - 1
        else:
            start_index = self.position.start_index

        if not self.is_right_edge():
            end_index = self.position.end_index + 1
        else:
            end_index = self.position.end_index

        nodes_above = []
        for position in range(start_index, end_index + 1):
            node_on_position = localize_node(mapped_engine=self.mapping, row_number=row_above, index=position)
            nodes_above.append(node_on_position)

        return nodes_above

    def nodes_below(self) -> list[Self] | None:
        """
        Coverage (1):
             - - - - - - - - - -
             - - - n o d e - - -
             - - 1 1 1 1 1 1 - -
        """
        if not self.is_bottom_edge():
            row_below = self.position.row_number + 1
        else:
            return None

        if not self.is_left_edge():
            start_index = self.position.start_index - 1
        else:
            start_index = self.position.start_index

        if not self.is_right_edge():
            end_index = self.position.end_index + 1
        else:
            end_index = self.position.end_index

        nodes_below = []
        for position in range(start_index, end_index + 1):
            node_on_position = localize_node(mapped_engine=self.mapping, row_number=row_below, index=position)
            nodes_below.append(node_on_position)

        return nodes_below

    def neighbors(self, unique=True):
        left_node = self.node_on_left()
        right_node = self.node_on_right()
        above_nodes = self.nodes_above() or []
        below_nodes = self.nodes_below() or []

        nodes_around = [left_node, right_node, *above_nodes, *below_nodes]
        nodes_around = [node for node in nodes_around if isinstance(node, Node)]

        if unique:
            return list(set(nodes_around))

        return nodes_around

    def adjacent_symbol_nodes(self) -> list[Self]:
        unique_neighbors = self.neighbors()
        symbol_nodes = [node for node in unique_neighbors if node.type == NodeTypeEnum.symbol]
        return symbol_nodes

    def is_engine_part(self) -> bool:
        if self.adjacent_symbol_nodes():
            return True

        return False

    def is_gear(self) -> tuple[bool, list[Self]]:
        # If this Node is star symbol
        if self.type == NodeTypeEnum.symbol and self.value == "*":
            # Get NUM neighbors
            unique_neighbors = self.neighbors()
            adjacent_parts = [node for node in unique_neighbors if node.type == NodeTypeEnum.num]

            # Has to have at least 2 num neighbor nodes
            if len(adjacent_parts) >= 2:
                return True, adjacent_parts

        return False, []

    def gear_ratio(self) -> int | None:
        is_gear, adjacent_parts = self.is_gear()
        if is_gear:
            adjacent_parts_values = [node.value for node in adjacent_parts]
            return reduce(mul, adjacent_parts_values)

        return None


def engine_row_mapping(engine_row: str, row_index: int):
    index_stack = []
    value_stack = []
    mapped_row = []

    for current_index, entity in enumerate(engine_row):
        # Is number
        if is_int(entity):
            # Append index and value to stacks...next value might be also number.
            index_stack.append(current_index)
            value_stack.append(str(entity))

            # If next_val is number, just iterate again and fulfill stacks...
            try:
                next_val = engine_row[current_index + 1]
            except IndexError:
                # Value is right edge. Example: .............=260
                next_val = None

            if is_int(next_val):
                continue

            # Until next_val is not a number
            else:
                # Record position from stack - first & last index of stack.
                new_position = NodePosition(row_number=row_index, start_index=index_stack[0], end_index=index_stack[-1])

                # Create new node with complete value from value stack.
                new_node = Node(value=int("".join(value_stack)), node_type=NodeTypeEnum.num, position=new_position)

                # Clear stack
                index_stack = []
                value_stack = []

        elif entity == ".":
            new_position = NodePosition(row_number=row_index, start_index=current_index, end_index=current_index)
            new_node = Node(value=entity, node_type=NodeTypeEnum.dot, position=new_position)
        else:
            new_position = NodePosition(row_number=row_index, start_index=current_index, end_index=current_index)
            new_node = Node(value=entity, node_type=NodeTypeEnum.symbol, position=new_position)

        # If node holds only one position. Its size = 1.
        if new_node.is_size_one():
            mapped_row.insert(new_node.position.start_index, new_node)
        # If node holds range of positions, insert it to every  position held. Its size > 1.
        else:
            for position in range(new_node.position.start_index, new_node.position.end_index + 1):
                mapped_row.insert(position, new_node)

    return mapped_row


def engine_mapping(engine_map: list[str]) -> MappedEngineT:
    mapped_engine = []
    for row_index, engine_row in enumerate(engine_map):
        mapped_row = engine_row_mapping(engine_row=engine_row, row_index=row_index)
        mapped_engine.append(mapped_row)

    return mapped_engine


def inject_mapping_to_node(mapped_engine: MappedEngineT):
    for row in mapped_engine:
        for node in row:
            node.mapping = mapped_engine


def find_engine_parts(mapped_engine: MappedEngineT) -> list[Node]:
    engine_parts = []
    for row in mapped_engine:
        for node in row:
            if node.type == NodeTypeEnum.num and node.is_engine_part():
                if node not in engine_parts:
                    engine_parts.append(node)

    return engine_parts


def find_gears(mapped_engine: MappedEngineT):
    gear_nodes = []
    for row in mapped_engine:
        for node in row:
            is_gear, num_nodes = node.is_gear()
            if is_gear:
                gear_nodes.append((node, num_nodes))

    return gear_nodes


if __name__ == "__main__":
    # Create mapped engine
    mapped_engine = engine_mapping(engine_map=input_engine)

    # Inject created mapping to every Node. Nodes are aware of the mapping they are part of...
    inject_mapping_to_node(mapped_engine=mapped_engine)

    # Set TEST NODE ZERO location on engine map and evaluate if it's a part of the engine.
    # Uncomment below for testing
    # test_node_0 = localize_node(mapped_engine=mapped_engine, row_number=0, index=27)
    # print("test node 0:", test_node_0)
    # print("is left edge:", test_node_0.is_left_edge())
    # print("is right edge", test_node_0.is_right_edge())
    # print("is top edge", test_node_0.is_top_edge())
    # print("Node on right:", test_node_0.node_on_right())
    # print("Node on left:", test_node_0.node_on_left())
    # print("above", test_node_0.nodes_above())
    # print("below", test_node_0.nodes_below())
    # print("neighbors not unique", test_node_0.neighbors(unique=False))
    # print("neighbors unique    ", test_node_0.neighbors())
    # print("symbol nodes:", test_node_0.adjacent_symbol_nodes())
    # print("is engine part?", test_node_0.is_engine_part())

    # Find Nodes which are engine parts
    engine_part_nodes = find_engine_parts(mapped_engine=mapped_engine)
    for node in engine_part_nodes:
        print(f"Part {node} adjacent to symbols: {node.adjacent_symbol_nodes()}")

    engine_part_nodes_values = [node.value for node in engine_part_nodes]
    print("Happy number:", sum(engine_part_nodes_values))

    # Part Two - find gears
    print("\nPart Two")
    gears = find_gears(mapped_engine=mapped_engine)
    ratios = []
    for gear in gears:
        gear_node, adjacent_parts = gear
        print(f"Gear {gear_node} adjacent to {adjacent_parts}")
        ratios.append(gear_node.gear_ratio())
    print("Happy number:", sum(ratios))
