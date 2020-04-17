from collections import OrderedDict


class Variables:
    def __init__(self, vars, neighbours, ptr=-1):
        self.vars = [x for x in vars]
        self.neighbours = neighbours
        self.ptrToCurr = ptr
        self.size = len(self.vars)
        self.values = OrderedDict()
        self.taken = [False for _ in self.vars]
        self.history = []

    def getCurrVar(self):
        return self.vars[self.ptrToCurr]

    def getNeighbours(self, var):
        return self.neighbours[var]

    def getNextVar(self, domains=None):  # if domains provided, the next var will be the one with the shortest domain
        self.history.append(self.ptrToCurr)
        if domains:
            free = []
            for i in range(self.size):
                if self.taken[i] == False:
                    free.append((self.vars[i], domains.getDomain(self.vars[i])))
            if len(free) == 0:
                return None
            nextVar = sorted(free, key=lambda x: len(x[1]))[0][0]
            self.ptrToCurr = self.vars.index(nextVar)
            self.taken[self.ptrToCurr] = True
            return nextVar
        else:
            if self.ptrToCurr + 1 == self.size:
                return None
            self.ptrToCurr += 1
            return self.vars[self.ptrToCurr]

    def hasValue(self, var):
        return var in self.values.keys()

    def assignValue(self, var, value):
        self.values[var] = value

    def getValue(self, var):
        return self.values[var]

    def getVarValDict(self):
        return self.values

    def stepBack(self):
        self.taken[self.ptrToCurr] = False
        self.ptrToCurr = self.history.pop()
        self.values.popitem()  # ?


class Domain:
    def __init__(self, arr, ptr=-1):
        self.vals = [x for x in arr]
        self.valsCopy = [x for x in arr]
        self.active = [True for _ in arr]
        self.ptrToCurr = ptr
        self.size = len(arr)

    def __len__(self):
        return sum(self.active)

    def undoRemoval(self, val):
        if val in self.vals:
            self.active[self.vals.index(val)] = True

    def restore(self):
        self.active = [True for _ in self.vals]
        self.ptrToCurr = -1

    def removeVal(self, val):
        if val in self.vals:
            self.active[self.vals.index(val)] = False

    def getValue(self):
        if self.ptrToCurr >= 0:
            return self.vals[self.ptrToCurr]

    def isEmpty(self):
        return sum(self.active) == 0

    def __iter__(self):
        self.ptrToCurr = -1
        return self

    def __next__(self):
        self.ptrToCurr += 1
        if self.ptrToCurr == self.size:
            raise StopIteration
        if self.active[self.ptrToCurr] == False:
            return self.__next__()
        return self.vals[self.ptrToCurr]


class Domains:
    def __init__(self, domains, ptr=-1):
        self.domains = OrderedDict()
        for var, values in domains.items():
            self.domains[var] = Domain(values)
        self.ptrToCurr = ptr
        self.size = len(self.domains)
        self.changeTags = []

    def getDomain(self, var):
        return self.domains[var]


class Constraint:
    def __init__(self, c):
        self.constraint = c

    def isSatisfied(self, vars):
        return self.constraint(vars)


class Constraints:
    def __init__(self, constraints):
        self.constraints = [Constraint(c) for c in constraints]
        self.size = len(self.constraints)

    def areAcceptable(self, vars):
        for c in self.constraints:
            if not c.isSatisfied(vars):
                return False
        return True

    def __iter__(self):
        self.ptrToCurr = -1
        return self

    def __next__(self):
        if self.ptrToCurr + 1 < self.size:
            self.ptrToCurr += 1
            return self.constraints[self.ptrToCurr]
        else:
            raise StopIteration


class CSP:
    def __init__(self, variables, domains, constraints, sdf=True):
        self.variables = variables
        self.domains = domains
        self.constraints = constraints
        self.sdf = sdf  # shortest domain first

    def backtrackSearch(self):
        return self._try(self.variables, self.domains)

    def _try(self, vars, domains):
        var = vars.getNextVar(domains if self.sdf else None)
        if var is None:
            return vars.getVarValDict()
        for value in domains.getDomain(var):
            vars.assignValue(var, value)
            if self.constraints.areAcceptable(vars.getVarValDict()):
                solution = self._try(vars, domains)
                if solution:
                    return solution
        domains.getDomain(var).restore()
        vars.stepBack()
        return False

    def forward(self):
        return self._forward(self.variables, self.domains)

    def _forward(self, vars, domains):
        var = vars.getNextVar(domains if self.sdf else None)
        if var is None:
            return vars.getVarValDict()
        for value in domains.getDomain(var):
            vars.assignValue(var, value)
            if self.constraints.areAcceptable(vars.getVarValDict()):
                if self._reduceDomains(vars, value, domains):
                    solution = self._forward(vars, domains)
                    if solution:
                        return solution
                self._restoreDomains(vars, value, domains)
        domains.getDomain(var).restore()
        vars.stepBack()
        return False

    def _reduceDomains(self, vars, val, domains):
        var = vars.getCurrVar()
        for neighbour in vars.getNeighbours(var):
            if not vars.hasValue(neighbour):
                domains.getDomain(neighbour).removeVal(val)
                if domains.getDomain(neighbour).isEmpty():
                    return False
        return True

    def _restoreDomains(self, vars, val, domains):
        var = vars.getCurrVar()
        for neighbour in vars.getNeighbours(var):
            if not vars.hasValue(neighbour):
                domains.getDomain(neighbour).undoRemoval(val)
