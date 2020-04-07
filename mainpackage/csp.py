from copy import deepcopy
from collections import OrderedDict


class Variables:
    def __init__(self, arr, ptr=-1):
        self.vars = [x for x in arr]
        self.ptrToCurr = ptr
        self.size = len(self.vars)

    def getNextVar(self):
        if self.ptrToCurr + 1 == self.size:
            return None
        self.ptrToCurr += 1
        return self.vars[self.ptrToCurr]

    def stepBack(self):
        if self.ptrToCurr >= 0:
            self.ptrToCurr -= 1

    def getVars(self):  # current included
        if self.ptrToCurr >= 0:
            return self.vars[0:self.ptrToCurr + 1]


class Domain:
    def __init__(self, arr, ptr=-1):
        self.vals = [x for x in arr]
        self.valsCopy = [x for x in arr]
        self.ptrToCurr = ptr
        self.size = len(arr)
        self.change_history = {}

    def undoLast(self, tag):
        if tag in self.change_history:
            self.vals, self.ptrToCurr, self.size = self.change_history[tag]
            del self.change_history[tag]  # possibly to delete

    def totalReset(self):
        self.vals = [x for x in self.valsCopy]
        self.size = len(self.vals)
        self.ptrToCurr = -1
        self.change_history = {}

    def removeByIdx(self, idx, tag):
        self.change_history[tag] = (self.vals[:], self.ptrToCurr, self.size)
        self.vals = self.vals[:idx] + self.vals[idx + 1:]
        self.ptrToCurr = min(self.ptrToCurr, len(self.vals) - 1)
        self.size = len(self.vals)

    def removeByVal(self, val, tag):
        if val in self.vals:
            self.change_history[tag] = (self.vals[:], self.ptrToCurr, self.size)
            self.vals.remove(val)
            self.ptrToCurr = min(self.ptrToCurr, len(self.vals) - 1)
            self.size = len(self.vals)

    def getByIdx(self, idx):
        self.ptrToCurr = idx
        return self.vals[idx]

    def getValue(self):
        if self.ptrToCurr >= 0:
            return self.vals[self.ptrToCurr]

    def isEmpty(self):
        return self.size == 0

    def __iter__(self):
        self.ptrToCurr = -1
        return self

    def __next__(self):
        if self.ptrToCurr + 1 < self.size:
            self.ptrToCurr += 1
            return self.getValue()
        else:
            raise StopIteration


class Domains:
    def __init__(self, domains, ptr=-1):
        self.domains = OrderedDict()
        for var, values in domains.items():
            self.domains[var] = Domain(values)
        self.ptrToCurr = ptr
        self.size = len(self.domains)
        self.changeTags = []

    def getNextDomain(self, var):
        if self.ptrToCurr == self.size:
            return None
        self.ptrToCurr += 1
        out = self.domains[var]
        return out

    def getDomain(self, var):
        return self.domains[var]

    def stepBack(self, var):
        if self.ptrToCurr >= 0:
            self.domains[var].totalReset()
            self.ptrToCurr -= 1

    def getCurrDom(self):
        if self.ptrToCurr >= 0:
            return self.domains[self.ptrToCurr]

    def getByIdx(self, idx):
        self.ptrToCurr = idx
        return self.domains[idx]

    def getValues(self):  # current included
        return [value.getValue() for var, value in self.domains.items()]

    def undoUpcoming(self):
        for i in range(self.ptrToCurr + 1, self.size):
            self.domains[i].undoLast(self.changeTags.pop())

    def anyUpcomingEmpty(self):
        for i in range(self.ptrToCurr + 1, self.size):
            if self.domains[i].isEmpty():
                return True
        return False


class Constraints:
    def __init__(self, constraints):
        self.constraints = constraints

    def areAcceptable(self, vars, domains):
        return self.constraints(vars, domains)


class CSP:
    def __init__(self, variables, domains, constraints):
        self.variables = variables
        self.domains = domains
        self.constraints = constraints

    def backtrackSearch(self):
        return self.try_(self.variables, self.domains)

    def try_(self, vars, domains):
        var = vars.getNextVar()
        if var is None:
            return vars.getVars(), domains.getValues()
        for value in domains.getNextDomain(var):
            if self.constraints.areAcceptable(vars.getVars(), domains):
                solution = self.try_(vars, domains)
                if solution:
                    return solution

        vars.stepBack()
        domains.stepBack(var)
        return False

    def forward(self, vars, doms, state):
        pass
