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
        self.puzzle=self.solution
        for row in self.puzzle:
            if len(set(row)) != self.size:
                return False

        for i in range(self.size):
            number_set = set()
            for j in range(self.size):
                number_set.add(self.puzzle[j][i])
            if len(number_set) != self.size:
                return False

        box_size = int(self.size ** 0.5)
        for i in range(box_size):
            for j in range(box_size):
                number_set = set()
                for row in range(box_size):
                    row_numbers = self.puzzle[i * box_size + row][j * box_size:(j + 1) * box_size]
                    for number in row_numbers:
                        number_set.add(number)
                if len(number_set) != self.size:
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
    constants = []
    for i in range(sudoku.size):
        for j in range(sudoku.size):
            if sudoku.puzzle != '.':
                constants.append((i, j))

    def get_next(i, j):
        j = j - 1
        if j < 0:
            j = sudoku.size - 1
            i -= 1
        return i, j

    def increment(i, j):
        if (i, j) in constants:
            increment(*get_next(i, j))
        current = int(sudoku.puzzle[i][j])
        current += 1
        if current >= 10:
            current = 1
            increment(*get_next(i, j))


# print(s.get_box_left_top_corner(2, 5))
print(s.check_victory())
