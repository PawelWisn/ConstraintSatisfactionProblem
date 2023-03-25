from mainpackage.csp import CSP, Variables, Constraints, Domains
from time import time
from collections import OrderedDict


class Board:
    def __init__(self, arr, h, v):
        self.state = self.arr_to_square(arr)
        self.size = int(len(arr) ** 0.5)
        self.h = h
        self.v = v

    def arr_to_square(self, arr):
        a = int(len(arr) ** 0.5)
        output = []
        for i in range(a):
            output.append(arr[a * i:a * (i + 1)])
        return output

    def fill_square(self, var, value):
        self.state[var[0]][var[1]] = str(value)

    def get_square(self, x, y):
        return self.state[x][y]

    def get_subrow(self, x, y, y2):
        return self.state[x][y:y2]

    def print_state(self):
        for row_idx, row in enumerate(self.state):
            if row_idx % (self.size // self.v) == 0 and row_idx:
                print('-' * (3 * self.size))
            for col_idx, square in enumerate(row):
                if col_idx % (self.size // self.h) == 0 and col_idx:
                    print('|', end=' ')
                print(square, end=' ')
            print()

        print()

    def dictToSquare(self, d):
        for x, y in d.items():
            self.fill_square(x, y)

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
        with open(filename, 'r') as f:
            f.readline()
            for i in range(1, id):
                f.readline()
            line = f.readline().strip().split(';')
            self.id = int(line[0])
            self.difficulty = float(line[1])
            self.horBoxes = int(line[3])
            self.verBoxes = int(line[4])
            self.puzzle = Board(list(line[2]), self.horBoxes, self.verBoxes)
            self.solution = Board(list(line[5]), self.horBoxes, self.verBoxes) if len(line) == 6 else None
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
        box_width = self.size // self.horBoxes
        box_height = self.size // self.verBoxes
        for i in range(self.verBoxes):
            for j in range(self.horBoxes):
                numbers = []
                for boxrow in range(box_height):
                    x, y, y2 = i * box_height + boxrow, j * box_width, (j + 1) * box_width
                    subrow_numbers = self.puzzle.get_subrow(x, y, y2)
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
                    variables.append((i, j))
                else:
                    domains[(i, j)] = [self.puzzle.get_square(i, j)]
                    variables = [(i, j)] + variables

        neighbours = dict()
        for i in range(self.size):
            for j in range(self.size):
                key = (i, j)
                row_n = [(i, col) for col in range(self.size)]
                col_n = [(row, j) for row in range(self.size)]
                row_n.remove(key)
                col_n.remove(key)
                box_x, box_y = self.get_box(i, j)
                box_n = []
                box_width = self.size // self.horBoxes
                box_height = self.size // self.verBoxes
                for box_x_offset in range(box_height):
                    for box_y_offset in range(box_width):
                        x, y = (box_x * box_height) + box_x_offset, (box_y * box_width) + box_y_offset
                        box_n.append((x, y))
                box_n.remove(key)
                neighbours[key] = tuple(sorted(set(box_n + row_n + col_n)))

        self.neighbours = neighbours
        self.variables = variables
        self.domains = domains

    def get_box(self, i, j):
        out = i // (self.size // self.verBoxes), j // (self.size // self.horBoxes)
        return out

    def constraint_row(self, vars):
        row, col = list(vars.items())[-1][0]  # new variable
        numbers_in_row = []
        for j in range(0, self.size):
            if (row, j) in vars.keys():  # row check
                numbers_in_row.append(vars[(row, j)])
        return len(numbers_in_row) == len(set(numbers_in_row))

    def constraint_col(self, vars):
        row, col = list(vars.items())[-1][0]  # new variable
        numbers_in_col = []
        for i in range(0, self.size):
            if (i, col) in vars.keys():  # column check
                numbers_in_col.append(vars[(i, col)])
        return len(numbers_in_col) == len(set(numbers_in_col))

    def constraint_box(self, vars):
        row, col = list(vars.items())[-1][0]  # new variable
        box_width = self.size // self.horBoxes
        box_height = self.size // self.verBoxes
        box_x, box_y = self.get_box(row, col)
        numbers_in_box = []
        for box_row_offset in range(box_height):
            x = box_x * box_height + box_row_offset  #
            for boxcol in range(box_y * box_width, (box_y + 1) * box_width):
                if (x, boxcol) in vars.keys():
                    numbers_in_box.append(vars[(x, boxcol)])
        return len(numbers_in_box) == len(set(numbers_in_box))


# example invoke
s = Sudoku(40)
s.puzzle.print_state()
vars = Variables(s.variables, s.neighbours)
domains = Domains(s.domains)
constraints = Constraints([s.constraint_row, s.constraint_col, s.constraint_box])
csp = CSP(vars, domains, constraints)
csp.backtrackSearch()
result = csp.backtrackForwardSearch()

s.puzzle.dictToSquare(result)
s.puzzle.print_state()
