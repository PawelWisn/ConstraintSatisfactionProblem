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
            self.variables = []
            self.setup_variables()
            self.domains = []
            self.setup_domains()

    def setup_variables(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.puzzle[i][j] == '.':
                    self.variables.append((i, j))

    def setup_domains(self):
        for i in range(len(self.variables)):
            self.domains.append([x for x in range(1, self.size + 1)])

    def get_box_left_top_corner(self, i, j):  # > v (row, column)
        a = int(self.size ** 0.5)
        return int(i // a * a), int(j // a * a)

    def constrains(self):
        for row in self.puzzle:  # rows
            numbers_in_row = []
            for number in row:
                if number != '.':
                    if number in numbers_in_row:
                        return False
                    else:
                        numbers_in_row.append(number)

        for i in range(self.size):  # columns
            numbers_in_col = []
            for j in range(self.size):
                number = self.puzzle[j][i]
                if number != '.':
                    if number in numbers_in_col:
                        return False
                    else:
                        numbers_in_col.append(number)

        box_size = int(self.size ** 0.5)  # boxes
        for i in range(box_size):
            for j in range(box_size):
                numbers_in_box = []
                for row in range(box_size):
                    subrow_numbers = self.puzzle[i * box_size + row][j * box_size:(j + 1) * box_size]
                    for number in subrow_numbers:
                        if number != '.':
                            if number in numbers_in_box:
                                return False
                            else:
                                numbers_in_box.append(number)

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


# print(s.get_box_left_top_corner(2, 5))
s = Sudoku(1)
s.print_solution()
s.print_puzzle()
