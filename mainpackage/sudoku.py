import numpy as np

def arr_to_square(arr):
    a = int(len(arr)**0.5)
    output = []
    for i in range(a):
        output.append(arr[a*i:a*(i+1)])
    return output

class Sudoku:

    def __init__(self, id, filename='src/Sudoku.csv'):
        with open(filename, 'r') as f:
            f.readline() # clear header
            for i in range(1, id):
                f.readline()
            line = f.readline().strip().split(';')
            self.id = int(line[0])
            self.diff = float(line[1])
            self.puzzle = arr_to_square(list(line[2]))
            self.solution = arr_to_square(list(line[3])) if len(line) == 4 else None

    def print_puzzle(self):
        for row in self.puzzle:
            print(row)
        print()

    def print_solution(self):
        if self.solution:
            for row in self.solution:
                print(row)
            print()

s = Sudoku(1)
# for row in s['puzzle']:
s.print_puzzle()
s.print_solution()
