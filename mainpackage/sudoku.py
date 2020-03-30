import numpy as np


def arr_to_square(arr):
    a = int(len(arr) ** 0.5)
    output = []
    for i in range(a):
        output.append(arr[a * i:a * (i + 1)])
    return output


class Sudoku:

    def __init__(self, id, filename='src/Sudoku.csv'):
        with open(filename, 'r') as f:
            f.readline()  # clear header
            for i in range(1, id):
                f.readline()
            line = f.readline().strip().split(';')
            self.id = int(line[0])
            self.diff = float(line[1])
            self.puzzle = arr_to_square(list(line[2]))
            self.solution = arr_to_square(list(line[3])) if len(line) == 4 else None
            self.size = int(len(list(line[2])) ** 0.5)

    def get_box_left_top_corner(self, i, j):  # > v (row, column)
        a = int(self.size ** 0.5)
        return int(i // a * a), int(j // a * a)

    def check_victory(self):
        expected_sum = int((1 + self.size) / 2 * self.size)
        for row in self.puzzle:
            total = sum(list(map(lambda x: int(x) if x != '.' else 0, row)))
            if total != expected_sum:
                return False

        for i in range(self.size):
            total = 0
            for j in range(self.size):
                total += int(self.puzzle[j][i]) if self.puzzle[j][i] != '.' else 0
            if total != expected_sum:
                return False

        box_size = int(self.size ** 0.5)
        for i in range(box_size):
            for j in range(box_size):
                total = 0
                for row in range(box_size):
                    total += sum(list(map(lambda x: int(x) if x != '.' else 0,
                                          self.puzzle[i * box_size + row][j * box_size:(j + 1) * box_size])))
                if total != expected_sum:
                    return False

        return True

    def print_puzzle(self):
        for row in self.puzzle:
            print(row)
        print()

    def print_solution(self):
        if self.solution:
            for row in self.solution:
                print(row)
            print()


s = Sudoku(1)
s.print_puzzle()


# s.print_solution()


def brute_force_sudoku(sudoku):
    pass


# print(s.get_box_left_top_corner(2, 5))
print(s.check_victory())
