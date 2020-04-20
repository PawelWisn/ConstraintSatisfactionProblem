from mainpackage.csp import CSP, Variables, Constraints, Domains
from time import time
import matplotlib.pyplot as plt
from copy import deepcopy


class Board:
    def __init__(self, matrix):
        self.state = matrix
        self.cp = matrix
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
        self.state = deepcopy(self.cp)
        for key, val in d.items():
            for idx, spot in enumerate(key):
                self.fill_square(spot, val[idx])

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
            self.board = Board([list(line.strip()) for line in f.readlines()])
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
        for var in vars:
            self.variables.append(tuple(var))
            self.domains[tuple(var)] = words[len(var)]

        self.neighbours = {}
        for var in self.variables:
            n = []
            for candidate in self.variables:
                if len(var) == len(candidate) and var is not candidate:
                    n.append(candidate)
            self.neighbours[var] = n

        self.varsAssignedToSquare = {}
        for i in range(len(self.board.state)):
            for j in range((len(self.board.state[0]))):
                if self.board.get_square(i, j) == '#':
                    continue
                temp = []
                for var in self.variables:
                    if (i, j) in var:
                        temp.append((var, var.index((i, j))))
                        if len(temp) == 2:
                            break
                self.varsAssignedToSquare[(i, j)] = temp

    def constraint_unique_word(self, vars):
        varList = list(vars.items())
        newVar, newVal = varList[-1]  # new variable
        if newVal in [val for var, val in varList[:-1]]:
            return False
        return True

    def constraint_word_fits(self, vars):
        newVar, newVal = list(vars.items())[-1]  # new variable
        for square in newVar:
            if len(self.varsAssignedToSquare[square]) == 2:
                (var1, idx1), (var2, idx2) = self.varsAssignedToSquare[square]
                if var1 in vars.keys():
                    if var2 in vars.keys():
                        if vars[var1][idx1] != vars[var2][idx2]:
                            return False
        return True


#example invoke
c = Crossword(1)
vars = Variables(c.variables, c.neighbours)
domains = Domains(c.domains)
constraints = Constraints([c.constraint_unique_word, c.constraint_word_fits])
csp = CSP(vars, domains, constraints)
csp.backtrackSearch()
csp.backtrackForwardSearch()
