from typing import List, Tuple, Callable
import random
from heapdict import heapdict
import time

from heuristic import Heuristics

PUZZLE_SIZE = 4


def if_solvable(puzzle: List[int]) -> bool:
    nr_of_inv = 0

    # count number of invertions
    for x in range(PUZZLE_SIZE * PUZZLE_SIZE - 1):
        for y in range(x + 1, PUZZLE_SIZE * PUZZLE_SIZE):
            if puzzle[x] and puzzle[y] and puzzle[x] > puzzle[y]:
                nr_of_inv += 1

    return nr_of_inv % 2 == 0  # if even, puzzle can be solved


def generate_puzzle(puzzleSize: int) -> Tuple[int]:
    puzzle = list(range(1, puzzleSize ** 2))  # create puzzle without 0

    while True:
        random.shuffle(puzzle)
        puzzle_with_zero = puzzle + [0]  # add 0 to the end of the shuffled puzzle

        if if_solvable(puzzle_with_zero):
            return tuple(puzzle_with_zero)


def random_move(row: int, col: int) -> Tuple[int, int]:
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
    dr, dc = random.choice(directions)
    return row + dr, col + dc


def generate_x_steps_ago(x: int) -> Tuple[int]:
    puzzle = generate_final_state()

    for _ in range(x):
        zero_index = puzzle.index(0)
        row, col = divmod(zero_index, PUZZLE_SIZE)
        new_row, new_col = random_move(row, col)

        while not (0 <= new_row < PUZZLE_SIZE and 0 <= new_col < PUZZLE_SIZE):
            new_row, new_col = random_move(row, col)

        new_index = new_row * PUZZLE_SIZE + new_col
        puzzle = list(puzzle)
        puzzle[zero_index], puzzle[new_index] = puzzle[new_index], puzzle[zero_index]

    return tuple(puzzle)


def reconstruct_path(came_from: dict, end_state: Tuple[int]) -> List[str]:
    path = []
    current = end_state

    while current in came_from:
        current, move = came_from[current]
        path.append(move)
    
    path.reverse()
    return path


def calculate_neighbour(state: Tuple[int]) -> List[Tuple[Tuple[int], str]]:
    neighbours = []
    zero_index = state.index(0)
    row, col = divmod(zero_index, PUZZLE_SIZE)

    moves = [("UP", -1, 0), ("DOWN", 1, 0), ("LEFT", 0, -1), ("RIGHT", 0, 1)]

    for move, dr, dc in moves:
        new_row, new_col = row + dr, col + dc

        if 0 <= new_row < PUZZLE_SIZE and 0 <= new_col < PUZZLE_SIZE:
            new_index = new_row * PUZZLE_SIZE + new_col
            
            state_as_list = list(state)
            state_as_list[zero_index], state_as_list[new_index] = state_as_list[new_index], state_as_list[zero_index]
            
            neighbours.append((tuple(state_as_list), move))
    
    return neighbours


# A*
def astar(start_puzzle: Tuple[int], heuristic: Callable[[Tuple[int]], int], final_state: Tuple[int]) -> Tuple[List[str], int]:
    came_from = {}
    open_set = heapdict()
    visited_set = set()

    start_g = 0
    g_score = {start_puzzle: 0}
    start_h = heuristic(start_puzzle)
    start_f = start_g + start_h

    open_set[start_puzzle] = start_f

    while open_set:
        current_puzzle, _ = open_set.popitem()
        g = g_score[current_puzzle]

        if current_puzzle in visited_set: continue
        
        visited_set.add(current_puzzle)

        if current_puzzle == final_state:
            path = reconstruct_path(came_from, current_puzzle)
            return path, len(visited_set)  # return path and how much we visited

        for neighbour, move in calculate_neighbour(current_puzzle):
            tentative_g = g + 1

            if tentative_g > 80: continue

            if neighbour not in g_score or tentative_g < g_score[neighbour]:
                g_score[neighbour] = tentative_g
                f = tentative_g + heuristic(neighbour)
                
                if neighbour not in open_set or f < open_set[neighbour]:
                    open_set[neighbour] = f

                came_from[neighbour] = (current_puzzle, move)

    return [], len(visited_set)


def generate_final_state() -> Tuple[int]:
    return tuple(list(range (1, PUZZLE_SIZE ** 2)) + [0])


def save_to_file(filename: str, data: List[str]) -> None:
    with open (filename, "a") as file:
        for d in data:
            file.write(" ".join(d) + "\n")


def run_experiment(n=1):
    final_state = generate_final_state()
    heuristic = Heuristics(final_state, PUZZLE_SIZE)
    result = []

    for i in range(n):
        puzzle = generate_puzzle(PUZZLE_SIZE)
        #puzzle = generate_x_steps_ago(200)
        #puzzle = (12, 1, 10, 2, 7, 11, 4, 14, 5, 9, 15, 8, 13, 3, 6, 0)
        print(f"---------Test {i + 1}---------")
        print("Puzzle:")
        for x in range(0, PUZZLE_SIZE ** 2, PUZZLE_SIZE):
            print(puzzle[x:x+PUZZLE_SIZE])
        for name, current_heuristic in [("manhattan_linear", heuristic.heuristic_manhattan_linear_conflict), ("manhattan", heuristic.heuristic_manhattan)]:
            start_time = time.time()
            path, visited = astar(puzzle, current_heuristic, final_state)
            duration = time.time() - start_time
            print(f"\nHeurystyka: {name}")
            print(f"Rozwiązanie (kroki): {path}")
            print(f"Liczba kroków do celu: {len(path)}")
            print(f"Liczba odwiedzonych stanów: {visited}")
            print(f"Czas działania: {duration:.4f} s")
            result.append([name, str(len(path)), str(visited), str(duration)])
            #save_to_file("result4x4", result)

if __name__ == "__main__":
    run_experiment()