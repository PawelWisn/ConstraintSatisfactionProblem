from mainpackage.csp import CSP, Variables, Constraints, Domains
from time import time
import matplotlib.pyplot as plt
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
            if row_idx % (self.size//self.v)==0 and row_idx:
                print('-'*(3*self.size))
            for col_idx, square in enumerate(row):
                if col_idx%(self.size//self.h)==0 and col_idx:
                    print('|',end=' ')
                print(square, end=' ')
            print()


        print()

    def dictToSquare(self, d):
        for x, y in d.items():
            s.puzzle.fill_square(x, y)

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
            self.puzzle = Board(list(line[2]), self.horBoxes,self.verBoxes)
            self.solution = Board(list(line[5]), self.horBoxes,self.verBoxes) if len(line) == 6 else None
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
                # print((i,j),box_n)
                box_n.remove(key)
                neighbours[key] = tuple(sorted(set(box_n + row_n + col_n)))

        self.neighbours = neighbours
        self.variables = variables
        self.domains = domains

    def sort_variables(self, low_to_high=True):
        self.domains = OrderedDict(sorted(self.domains.items(), key=lambda x: len(x[1]), reverse=not low_to_high))
        self.variables = [var for var, dom in self.domains.items()]

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


first =1
last = 33
skip = 3
times_bt = []
times_bt_f = []
times_bt_sdf = []
times_bt_f_sdf = []
i_arr = set()
info = ["BT", "BT + SDF", "BT + FC", "BT + FC + SDF"]
for run in range(len(info)):
    if run==1:continue
    print("+" * 90, "RUN:", info[run])
    # for i in range(first, last + 1, skip):
    # for i in [1,7,17,25,29,32,39]:
    for i in [56]:
        i_arr.add(i)
        s = Sudoku(i)

        sdf = run % 2

        vars = Variables(s.variables, s.neighbours)
        domains = Domains(s.domains)
        constraints = Constraints([s.constraint_row, s.constraint_col, s.constraint_box])
        csp = CSP(vars, domains, constraints, sdf)

        print('=' * 40, info[run], s.id)

        s.puzzle.print_state()

        start = time()
        if run <= 1:
            sol = csp.backtrackSearch()
        else:
            sol = csp.forward()
        end = time()

        if sol:
            s.puzzle.dictToSquare(sol)
            s.puzzle.print_state()
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

        print('time: %.10f\n' % (end - start))

# width = 0.2
# i_arr = [i+1 for i in range(len(i_arr))]
# if len(info) > 0:
#     if len(times_bt) > 0:
#         plt.bar([x - 1.5 * width for x in sorted(list(i_arr))], times_bt, width=width, align='center', color='#00bb00',
#                 label=info[0])
#     if len(info) > 1:
#         if len(times_bt_sdf) > 0:
#             plt.bar([x - width / 2 for x in sorted(list(i_arr))], times_bt_sdf, width=width, align='center',
#                     color='green',
#                     label=info[1])
#     if len(info) > 2:
#         if len(times_bt_f) > 0:
#             plt.bar([x+width / 2 for x in sorted(list(i_arr))], times_bt_f, width=width, align='center',
#                     color='#ff0000',
#                     label=info[2])
#     if len(info) > 3:
#         if len(times_bt_f_sdf) > 0:
#             plt.bar([x + 1.5 * width for x in sorted(list(i_arr))], times_bt_f_sdf, width=width, align='center',
#                     color='#ba0000',
#                     label=info[3])
#     plt.xticks(sorted(list(i_arr)))
#     plt.xlabel("Sudoku number")
#     plt.ylabel("Time [s]")
#     plt.legend()
#     plt.show()

width = 0.2
i_arr = [i+2 for i in range(len(i_arr))]
if len(info) > 0:
    if len(times_bt) > 0:
        plt.bar([x - 1 * width for x in sorted(list(i_arr))], times_bt, width=width, align='center', color='#00bb00',
                label=info[0])
    if len(info) > 1:
        if len(times_bt_sdf) > 0:
            plt.bar([x - width / 2 for x in sorted(list(i_arr))], times_bt_sdf, width=width, align='center',
                    color='green',
                    label=info[1])
    if len(info) > 2:
        if len(times_bt_f) > 0:
            plt.bar([x for x in sorted(list(i_arr))], times_bt_f, width=width, align='center',
                    color='#ff0000',
                    label=info[2])
    if len(info) > 3:
        if len(times_bt_f_sdf) > 0:
            plt.bar([x + 1 * width for x in sorted(list(i_arr))], times_bt_f_sdf, width=width, align='center',
                    color='#ba0000',
                    label=info[3])
    plt.xticks(sorted(list(i_arr)))
    plt.xlabel("Sudoku number")
    plt.ylabel("Time [s]")
    plt.legend()
    plt.show()


def speedup(one, two):
    return float(round(round(one / two, 4), 2))


speedups = []
for bt, f, f_sdf in zip(times_bt,times_bt_f,times_bt_f_sdf):
    speedups.append((speedup(bt,bt), speedup(bt,f), speedup(bt,f_sdf)))
    print(*speedups[-1],sep=' ',end='\n')
def avg(speedps):
    one = two = three = four = 0
    for line in speedps:
        one += line[0]
        #two += line[1]
        three += line[1]
        four += line[2]
    one /= len(speedps)
    #two /= len(speedps) if len(speedps) else 1
    three /= len(speedps)
    four /= len(speedps)
    return round(one,2),round(three,2),round(four,2)
print('avg speedup:', avg(speedups))
