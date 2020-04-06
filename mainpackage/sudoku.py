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

    def update(self, var, val):
        if var and val:
            if var not in self.change_history.keys():
                initial = self.get_square(var[0], var[1])
                self.change_history[var] = (initial, val)
            self.fill_square(var, val)

    def fill_square(self, var, value):
        self.state[var[0]][var[1]] = str(value)

    def downgrade(self):
        try:
            var, vals = self.change_history.popitem()
            initial, _ = vals
            self.fill_square(var, initial)
        except KeyError:
            pass

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
            self.constraints = [self.constraint_box, self.constraint_row, self.constraint_column]
            self.create_variables()
            self.create_domains()

    def create_variables(self):
        variables = []
        for i in range(self.size):
            for j in range(self.size):
                if self.puzzle.get_square(i, j) == '.':
                    variables.append((i, j))
        self.variables = variables

    def create_domains(self):
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

        domains = []
        for i in range(self.size):
            for j in range(self.size):
                if self.puzzle.get_square(i, j) == '.':
                    domain = []
                    candidates = [str(x) if x < 10 else chr(55 + x) for x in range(1, self.size + 1)]
                    for x in candidates:
                        if x not in row_numbers[i] and x not in column_numbers[j] and x not in box_numbers[
                            self.get_box(i, j)]:
                            domain.append(x)
                    domains.append(domain)

        self.domains = domains

    def sort_variables(self, low_to_high=True):
        zipped = zip(self.variables, self.domains)
        self.variables = []
        self.domains = []
        for var, dom in sorted(zipped, key=lambda x: len(x[1]), reverse=not low_to_high):
            self.variables.append(var)
            self.domains.append(dom)
            # print(var,dom)

    def get_box(self, i, j):  # > v (row, column)
        a = int(self.size ** 0.5)
        out = int(i // a), int(j // a)
        return out

    def constraint_row(self, state):
        for row in state:
            numbers_in_row = []
            for number in row:
                if number != '.':
                    if number in numbers_in_row:
                        return False
                    else:
                        numbers_in_row.append(number)
        return True

    def constraint_column(self, state):
        for i in range(state.size):
            numbers_in_col = []
            for j in range(state.size):
                number = state.get_square(j, i)
                if number != '.':
                    if number in numbers_in_col:
                        return False
                    else:
                        numbers_in_col.append(number)
        return True

    def constraint_box(self, state):
        box_size = int(state.size ** 0.5)
        for i in range(box_size):
            for j in range(box_size):
                numbers_in_box = []
                for boxrow in range(box_size):
                    subrow_numbers = state.get_subrow(i * box_size + boxrow, j * box_size, (j + 1) * box_size)
                    for number in subrow_numbers:
                        if number != '.':
                            if number in numbers_in_box:
                                return False
                            else:
                                numbers_in_box.append(number)
        return True


first = 3
last = 3
times = []
times_s = []
times_r = []
i_arr = set()
info = ["Unsorted","Sorted"]
for run in range(len(info)):
    # if run==0:
    #     continue
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ RUN:", info[run])
    for i in range(first, last + 1,3):
        i_arr.add(i)
        s = Sudoku(i)
        if run == 1:
            s.sort_variables()
        if run == 2:
            s.sort_variables(False)
        vars = Variables(s.variables)
        doms = Domains(s.domains)
        cons = Constraints(s.constraints)
        csp = CSP(vars, doms, cons, s.puzzle)

        print(info[run], '-----------------------------', s.id)

        # s.puzzle.print_state()

        start = time()
        sol = csp.backtrackSearch()
        end = time()
        if run == 0:
            times.append(end - start)
        if run == 1:
            times_s.append(end - start)
        if run == 2:
            times_r.append(end - start)

        print('time: %.10f' % (end - start))

        if sol:
            # print(sol[0], '\n')
            sol[1].print_state()
        else:
            print("NO SOLUTION")

if len(info) > 0:
    if len(times)>0:
        plt.bar([x - 0.1 for x in list(i_arr)], times, width=0.2, align='center', color='blue',
                label="Unsorted")
    if len(info)>1:
        if len(times_s)>0:
            plt.bar([x + 0.1 for x in list(i_arr)], times_s, width=0.2, align='center', color='orange',
                    label="Sorted")
    if len(info)>2:
        if len(times_r)>0:
            plt.bar([x + 0.3 for x in list(i_arr)], times_r, width=0.2, align='center', color='red',
                    label="Sorted Backwards")
    plt.xticks(list(i_arr))
    plt.xlabel("Puzzle number")
    plt.ylabel("Time [s]")
    plt.legend()
    plt.show()
