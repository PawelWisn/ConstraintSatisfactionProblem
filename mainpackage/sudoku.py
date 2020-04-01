from csp import CSP, Variables, Constraints, Domains
from time import time


class Board:
    def __init__(self, arr):
        self.state = self.arr_to_square(arr)
        self.size = int(len(arr) ** 0.5)
        self.change_history = []

    def arr_to_square(self, arr):
        a = int(len(arr) ** 0.5)
        output = []
        for i in range(a):
            output.append(arr[a * i:a * (i + 1)])
        return output

    def update(self, vars, vals=None):
        if vars and vals:
            self.fill_square(var=vars[-1], val=vals[-1])
        elif vars:
            self.fill_square(vars[-1], '.')

    def fill_square(self, var, val):
        self.state[var[0]][var[1]] = str(val)
        # if var not in self.change_history and val!=".":
        #    self.change_history.append(var)

    # def reset_last(self):
    #     if len(self.change_history) > 0:
    #         var = self.change_history[-1]
    #         self.change_history = self.change_history[:-1]
    #         self.fill_square(var, '.')

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

    def create_variables(self):
        variables = []
        for i in range(self.size):
            for j in range(self.size):
                if self.puzzle.get_square(i, j) == '.':
                    variables.append((i, j))
        return variables

    def create_domains(self):
        domains = []
        for i in range(self.size):
            for j in range(self.size):
                if self.puzzle.get_square(i, j) == '.':
                    domains.append([str(x) for x in range(1, self.size + 1)])
        return domains

    # def get_box_left_top_corner(self, i, j):  # > v (row, column)
    #     a = int(self.size ** 0.5)
    #     return int(i // a * a), int(j // a * a)

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

    def solution_complete(self, state):
        for row in state:  # rows
            if '.' in row or len(set(row)) != state.size:
                return False

        for i in range(state.size):  # columns
            number_set = set()
            for j in range(state.size):
                if state.get_square(j, i) == '.':
                    return False
                number_set.add(state.get_square(j, i))
            if len(number_set) != state.size:
                return False

        box_size = int(state.size ** 0.5)  # boxes
        for i in range(box_size):
            for j in range(box_size):
                number_set = set()
                for boxrow in range(box_size):
                    row_numbers = state.get_subrow(i * box_size + boxrow, j * box_size, (j + 1) * box_size)
                    for number in row_numbers:
                        if number == '.':
                            return False
                        number_set.add(number)
                if len(number_set) != state.size:
                    return False

        return True


# s = Sudoku(1)
# s.puzzle.print_state()
# s.solution.print_state()
#
# vars = Variables(s.create_variables())
# doms = Domains(s.create_domains())
# cons = Constraints([s.constraint_row, s.constraint_column, s.constraint_box])

for i in range(1,44):

    s = Sudoku(i)
    vars = Variables(s.create_variables())
    doms = Domains(s.create_domains())
    cons = Constraints([s.constraint_row, s.constraint_column, s.constraint_box])
    csp = CSP(vars, doms, cons, s.solution_complete, s.puzzle)

    start = time()
    sol = csp.backtrack_search()
    end = time()

    print('-----------------------\n',s.id,'- time:', end - start, '\n', sol[0])
    sol[1].print_state()
    print()
    # s.solution.print_state()
