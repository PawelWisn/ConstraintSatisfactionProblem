from csp import CSP, Variables, Constraints, Domains
from time import time
import matplotlib.pyplot as plt
from collections import OrderedDict


class Board:
    def __init__(self, arr):
        self.state = self.arr_to_square(arr)
        self.size = int(len(arr) ** 0.5)
        self.change_history = OrderedDict()

    def arr_to_square(self, arr):
        a = int(len(arr) ** 0.5)
        output = []
        for i in range(a):
            output.append(arr[a * i:a * (i + 1)])
        return output

    # def update(self, var, val):
    #     if var and val:
    #         if var not in self.change_history.keys():
    #             initial = self.get_square(var[0], var[1])
    #             self.change_history[var] = (initial, val)
    #         self.fill_square(var, val)

    def fill_square(self, var, value):
        self.state[var[0]][var[1]] = str(value)

    # def downgrade(self):
    #     try:
    #         var, vals = self.change_history.popitem()
    #         initial, _ = vals
    #         self.fill_square(var, initial)
    #     except KeyError:
    #         pass

    def get_square(self, x, y):
        return self.state[x][y]

    def get_subrow(self, x, y, y2):
        return self.state[x][y:y2]

    def print_state(self):
        for row in self.state:
            print(row)
        print()

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < self.size:
            self.index += 1
            return self.state[self.index - 1]
        else:
            raise StopIteration


class Sudoku:
    def __init__(self, id, filename='src/Sudoku.csv'):
        super().__init__()
        with open(filename, 'r') as f:
            f.readline()  # clear header
            for i in range(1, id):
                f.readline()
            line = f.readline().strip().split(';')
            self.id = int(line[0])
            self.difficulty = float(line[1])
            self.puzzle = Board(list(line[2]))
            self.solution = Board(list(line[3])) if len(line) == 4 else None
            self.size = int(len(list(line[2])) ** 0.5)
            self.create_vars_doms()

    def create_vars_doms(self):
        row_numbers = []
        for row in self.puzzle:
            numbers = []
            for number in row:
                if number != '.':
                    numbers.append(number)
            row_numbers.append(numbers)

        column_numbers = []
        for i in range(self.size):
            numbers = []
            for j in range(self.size):
                number = self.puzzle.get_square(j, i)
                if number != '.':
                    numbers.append(number)
            column_numbers.append(numbers)

        box_numbers = {}
        box_size = int(self.puzzle.size ** 0.5)
        for i in range(box_size):
            for j in range(box_size):
                numbers = []
                for boxrow in range(box_size):
                    subrow_numbers = self.puzzle.get_subrow(i * box_size + boxrow, j * box_size, (j + 1) * box_size)
                    for number in subrow_numbers:
                        if number != '.':
                            numbers.append(number)
                box_numbers[(i, j)] = numbers

        domains = OrderedDict()
        variables = []
        for i in range(self.size):
            for j in range(self.size):
                if self.puzzle.get_square(i, j) == '.':
                    domain = []
                    candidates = [str(x) if x < 10 else chr(55 + x) for x in range(1, self.size + 1)]
                    for x in candidates:
                        if x not in row_numbers[i] and x not in column_numbers[j] and x not in box_numbers[
                            self.get_box(i, j)]:
                            domain.append(x)
                    domains[(i, j)] = domain
                else:
                    domains[(i, j)] = [self.puzzle.get_square(i, j)]
                variables.append((i, j))

        self.domains = domains

    def sort_variables(self, low_to_high=True):
        self.domains = OrderedDict(sorted(self.domains.items(), key=lambda x: len(x[1]), reverse=not low_to_high))

    def get_box(self, i, j):  # > v (row, column)
        a = int(self.size ** 0.5)
        return int(i // a), int(j // a)

    def constraints(self, vars, domains):
        row, col = vars[-1]  # new variable

        numbers_in_row = []
        numbers_in_col = []
        for j in range(0, self.size):
            if (row, j) in vars:  # row check
                numbers_in_row.append(domains[(row, j)].getValue())
            if (j, col) in vars:  # column check
                numbers_in_col.append(domains[(j, col)].getValue())
        if len(numbers_in_row) != len(set(numbers_in_row)):
            return False
        if len(numbers_in_col) != len(set(numbers_in_col)):
            return False

        box_size = int(self.size ** 0.5)
        box_x, box_y = self.get_box(row, col)
        numbers_in_box = []
        for boxrow in range(box_size):  # box check
            x = box_x * box_size + boxrow
            y = box_x * box_size
            y2 = (box_y + 1) * box_size
            for boxcol in range(y, y2):
                if (x, boxcol) in vars:
                    numbers_in_box.append(domains[(x, boxcol)].getValue())
        if len(numbers_in_box) != len(set(numbers_in_box)):
            return False
        return True


s = Sudoku(1)
s.puzzle.print_state()
s.sort_variables()
pass
