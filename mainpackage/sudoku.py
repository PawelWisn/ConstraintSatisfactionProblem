from mainpackage.csp import CSP, Variables, Constraints, Domains
from time import time
import matplotlib.pyplot as plt
from collections import OrderedDict


class Board:
    def __init__(self, arr):
        self.state = self.arr_to_square(arr)
        self.size = int(len(arr) ** 0.5)

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
            f.readline()
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

        self.variables = variables
        self.domains = domains

    def sort_variables(self, low_to_high=True):
        self.domains = OrderedDict(sorted(self.domains.items(), key=lambda x: len(x[1]), reverse=not low_to_high))
        self.variables = [var for var, dom in self.domains.items()]

    def get_box(self, i, j):
        a = int(self.size ** 0.5)
        return int(i // a), int(j // a)

    def constraint_row(self, vars):
        row, col = list(vars.items())[-1][0]  # new variable
        numbers_in_row = []
        for j in range(0, self.size):
            if (row, j) in vars.keys():  # row check
                numbers_in_row.append(vars[(row,j)])
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
        box_size = int(self.size ** 0.5)  # box check
        box_x, box_y = self.get_box(row, col)
        numbers_in_box = []
        for boxrow in range(box_size):
            x = box_x * box_size + boxrow
            for boxcol in range(box_y * box_size, (box_y + 1) * box_size):
                if (x, boxcol) in vars.keys():
                    numbers_in_box.append(vars[(x, boxcol)])
        return len(numbers_in_box) == len(set(numbers_in_box))


first = 13
last = 13
times = []
times_s = []
times_r = []
i_arr = set()
info = ["Backtrack", "Backtrack - Smallest Domain First"]
for run in range(len(info)):
    # if run==0:
    #     continue
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ RUN:", info[run])
    for i in range(first, last + 1, 1):
        i_arr.add(i)
        s = Sudoku(i)

        if run == 1:
            s.sort_variables()
        if run == 2:
            s.sort_variables(False)
        vars = Variables(s.variables)
        domains = Domains(s.domains)
        constraints = Constraints([s.constraint_row, s.constraint_col, s.constraint_box])
        csp = CSP(vars, domains, constraints)

        print(info[run], '-----------------------------', s.id)

        s.puzzle.print_state()

        start = time()
        # sol = csp.forward()
        sol = csp.backtrackSearch()
        end = time()

        if sol:
            for x, y in sol.items():
                s.puzzle.fill_square(x, y)
            s.puzzle.print_state()
        else:
            print("NO SOLUTION")

        if run == 0:
            times.append(end - start)
        if run == 1:
            times_s.append(end - start)
        if run == 2:
            times_r.append(end - start)

        print('time: %.10f\n' % (end - start))

if len(info) > 0:
    if len(times) > 0:
        plt.bar([x - 0.1 for x in list(i_arr)], times, width=0.2, align='center', color='blue',
                label=info[0])
    if len(info) > 1:
        if len(times_s) > 0:
            plt.bar([x + 0.1 for x in list(i_arr)], times_s, width=0.2, align='center', color='orange',
                    label=info[1])
    if len(info) > 2:
        if len(times_r) > 0:
            plt.bar([x + 0.3 for x in list(i_arr)], times_r, width=0.2, align='center', color='red',
                    label=info[2])
    plt.xticks(list(i_arr))
    plt.xlabel("Puzzle number")
    plt.ylabel("Time [s]")
    plt.legend()
    plt.show()
