from mainpackage.csp import CSP, Variables, Constraints, Domains
from time import time
import matplotlib.pyplot as plt
from collections import OrderedDict
from copy import deepcopy
from math import log2


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

    def reset_fill(self, vars):
        self.board.dictToSquare(vars)
        self.board.print_state()

    # def sort_variables(self, low_to_high=True):
    #     self.domains = OrderedDict(sorted(self.domains.items(), key=lambda x: len(x[1]), reverse=not low_to_high))
    #     self.variables = [var for var, dom in self.domains.items()]
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


printAllowed = True
first = 20
last = 20
skip = 1
times_bt = []
times_bt_f = []
times_bt_sdf = []
times_bt_f_sdf = []
i_arr = set()
info = ["Backtrack", "Backtrack - SDF", "Forward", "Forward - SDF"]
for run in range(len(info)):
    # if run ==0 or run==2:
    #     continue
    print("+" * 90, "RUN:", info[run])
    for i in range(first, last + 1, skip):
        # if i == 3:
        #     continue
        i_arr.add(i)
        c = Crossword(i)

        sdf = run % 2

        vars = Variables(c.variables, c.neighbours)
        domains = Domains(c.domains)
        constraints = Constraints([c.constraint_unique_word, c.constraint_word_fits])
        csp = CSP(vars, domains, constraints, sdf)

        if printAllowed: print('-' * 40, info[run], i)

        start = time()
        if run <= 1:
            sol = csp.backtrackSearch()
        else:
            sol = csp.forward()
        end = time()

        if printAllowed:
            if sol:
                c.board.dictToSquare(sol)
                c.board.print_state()
            else:
                print("NO SOLUTION")

            diff = end - start
            if run == 0:
                times_bt.append(diff)
            if run == 2:
                times_bt_f.append(diff)
            if run == 1:
                times_bt_sdf.append(diff)
            if run == 3:
                times_bt_f_sdf.append(diff)

            if printAllowed: print('time: %.10f\n' % (end - start))

width = 0.2
if len(info) > 0:
    if len(times_bt) > 0:
        plt.bar([x - 1.5 * width for x in sorted(list(i_arr))], times_bt, width=width, align='center',
                color='#00bb00',
                label=info[0])
    if len(info) > 1:
        if len(times_bt_sdf) > 0:
            plt.bar([x - width / 2 for x in sorted(list(i_arr))], times_bt_sdf, width=width, align='center',
                    color='green',
                    label=info[1])
    if len(info) > 2:
        if len(times_bt_f) > 0:
            plt.bar([x + width / 2 for x in sorted(list(i_arr))], times_bt_f, width=width, align='center',
                    color='#ff0000',
                    label=info[2])
    if len(info) > 3:
        if len(times_bt_f_sdf) > 0:
            plt.bar([x + 1.5 * width for x in sorted(list(i_arr))], times_bt_f_sdf, width=width, align='center',
                    color='#ba0000',
                    label=info[3])
    plt.xticks(sorted(list(i_arr)))
    plt.xlabel("Crossword number")
    plt.ylabel("Time [s]")
    plt.legend()
    plt.show()


def speedup(one, two):
    return str(round(round(one / two, 4) * 100 - 100, 4)) + '%'


stats = []
speedups = []
for one, two in zip(times_bt, times_bt_f):
    speedups.append(float(speedup(one, two)[:-1]))
    stats.append((round(one, 4), round(two, 4), speedup(one, two)))
    print(stats[-1])
print('avg speedup:', str(round(sum(speedups) / len(speedups), 2)) + '%')
