from mainpackage.csp import CSP, Variables, Constraints, Domains
from time import time
import matplotlib.pyplot as plt
from collections import OrderedDict


class Board:
    def __init__(self, matrix):
        self.state = matrix
        self.width = len(matrix[0])
        self.height = len(matrix)

    def fill_square(self, var, value):
        self.state[var[0]][var[1]] = str(value)

    def get_square(self, x, y):
        return self.state[x][y]

    def get_subrow(self, x, y, y2):
        return self.state[x][y:y2]

    def print_state(self):
        for row in self.state:
            print(row)
        print()

    def dictToSquare(self, d):
        for x, y in d.items():
            self.fill_square(x, y)

    def __iter__(self):
        return self

    def __next__(self):
        for row in self.state:
            return row
        raise StopIteration


class Crossword:
    def __init__(self, id):
        board = f'src/Jolka/puzzle{id}'
        words = f'src/Jolka/words{id}'
        with open(board, 'r') as f:
            self.board = Board([line.strip() for line in f.readlines()])
        with open(words, 'r') as f:
            self.words = sorted([line.strip() for line in f.readlines()])

        self.create_vars_doms()

    def create_vars_doms(self):

        horVars = {}
        for i in range(self.board.height):
            prev = '#'
            for j in range(self.board.width):
                if prev == '#' \
                        and self.board.get_square(i, j) == '_' \
                        and j < self.board.width - 1 \
                        and self.board.get_square(i, j + 1) == '_':
                    var_x, var_y = i, j
                    horVars[(i, j)] = [(i, j)]
                elif prev == '_' and self.board.get_square(i, j) == '_':
                    horVars[(var_x, var_y)].append((i, j))
                prev = self.board.get_square(i, j)
        print(horVars.items())

        verVars = {}
        for j in range(self.board.width):
            prev = '#'
            for i in range(self.board.height):
                if prev == '#' \
                        and self.board.get_square(i, j) == '_' \
                        and i < self.board.height - 1 \
                        and self.board.get_square(i + 1, j) == '_':
                    var_x, var_y = i, j
                    verVars[(i, j)] = [(i, j)]
                elif prev == '_' and self.board.get_square(i, j) == '_':
                    verVars[(var_x, var_y)].append((i, j))
                prev = self.board.get_square(i, j)
        print(verVars.items())

        vars = list([items for key, items in verVars.items()])
        vars.extend([items for key, items in horVars.items()])

        words = {}
        for word in self.words:
            if len(word) in words.keys():
                words[len(word)].append(word)
            else:
                words[len(word)] = [word]

        self.domains = {}
        self.variables = []
        for var in sorted(vars, key=lambda x: len(x)):
            self.variables.append(tuple(var))
            self.domains[tuple(var)] = words[len(var)]

        self.neighbours = {}
        for var in self.variables:
            n = []
            for candidate in self.variables:
                if len(var) == len(candidate) and var is not candidate:
                    n.append(candidate)
            self.neighbours[var] = n
        pass

    # def sort_variables(self, low_to_high=True):
    #     self.domains = OrderedDict(sorted(self.domains.items(), key=lambda x: len(x[1]), reverse=not low_to_high))
    #     self.variables = [var for var, dom in self.domains.items()]
    #
    # def get_box(self, i, j):
    #     out = i // (self.size // self.verBoxes), j // (self.size // self.horBoxes)
    #     return out
    #
    # def constraint_row(self, vars):
    #     row, col = list(vars.items())[-1][0]  # new variable
    #     numbers_in_row = []
    #     for j in range(0, self.size):
    #         if (row, j) in vars.keys():  # row check
    #             numbers_in_row.append(vars[(row, j)])
    #     return len(numbers_in_row) == len(set(numbers_in_row))
    #
    # def constraint_col(self, vars):
    #     row, col = list(vars.items())[-1][0]  # new variable
    #     numbers_in_col = []
    #     for i in range(0, self.size):
    #         if (i, col) in vars.keys():  # column check
    #             numbers_in_col.append(vars[(i, col)])
    #     return len(numbers_in_col) == len(set(numbers_in_col))
    #
    # def constraint_box(self, vars):
    #     row, col = list(vars.items())[-1][0]  # new variable
    #     box_width = self.size // self.horBoxes
    #     box_height = self.size // self.verBoxes
    #     box_x, box_y = self.get_box(row, col)
    #     numbers_in_box = []
    #     for box_row_offset in range(box_height):
    #         x = box_x * box_height + box_row_offset  #
    #         for boxcol in range(box_y * box_width, (box_y + 1) * box_width):
    #             if (x, boxcol) in vars.keys():
    #                 numbers_in_box.append(vars[(x, boxcol)])
    #     return len(numbers_in_box) == len(set(numbers_in_box))


c = Crossword(1)
c.board.print_state()
