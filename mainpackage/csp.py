from collections import OrderedDict


class Variables:
    def __init__(self, arr, ptr=-1):
        self.vars = [x for x in arr]
        self.ptrToCurr = ptr
        self.size = len(self.vars)
        self.values = OrderedDict()

    def getCurrVar(self):
        if self.ptrToCurr >= 0:
            return self.vars[self.ptrToCurr]

    def getNextVar(self):
        if self.ptrToCurr + 1 == self.size:
            return None
        self.ptrToCurr += 1
        return self.vars[self.ptrToCurr]

    def assignValue(self,var, value):
        self.values[var] = value

    def getValue(self, var):
        return self.values[var]

    def getVarValDict(self):
        return self.values

    def stepBack(self):
        if self.ptrToCurr >= 0:
            self.ptrToCurr -= 1
            self.values.popitem()

    def getActiveVars(self):  # current included
        if self.ptrToCurr >= 0:
            return self.vars[0:self.ptrToCurr + 1]


class Domain:
    def __init__(self, arr, ptr=-1):
        self.vals = [x for x in arr]
        self.valsCopy = [x for x in arr]
        self.ptrToCurr = ptr
        self.size = len(arr)
        # self.change_history = {}

    # def undoLast(self, tag):
    #     if tag in self.change_history:
    #         self.vals, self.ptrToCurr, self.size = self.change_history[tag]
    #         del self.change_history[tag]  # possibly to delete

    def restore(self, ptr=True):
        self.vals = [x for x in self.valsCopy]
        self.size = len(self.vals)
        if ptr:
            self.ptrToCurr = -1
        # self.change_history = {}

    # def removeByIdx(self, idx, tag):
    #     self.change_history[tag] = (self.vals[:], self.ptrToCurr, self.size)
    #     self.vals = self.vals[:idx] + self.vals[idx + 1:]
    #     self.ptrToCurr = min(self.ptrToCurr, len(self.vals) - 1)
    #     self.size = len(self.vals)

    def removeByVal(self, val):
        if val in self.vals:
            # self.change_history[tag] = (self.vals[:], self.ptrToCurr, self.size)
            self.vals.remove(val)
            self.ptrToCurr = min(self.ptrToCurr, len(self.vals) - 1)
            self.size = len(self.vals)

    # def getByIdx(self, idx):
    #     self.ptrToCurr = idx
    #     return self.vals[idx]

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
            return self.vals[self.ptrToCurr]
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

    def getDomain(self, var):
        return self.domains[var]

    # def stepBack(self, var):
    #     if self.ptrToCurr >= 0:
    #         self.domains[var].totalReset()
    #         self.ptrToCurr -= 1

    # def getCurrDom(self):
    #     if self.ptrToCurr >= 0:
    #         return self.domains[self.ptrToCurr]

    # def getValues(self):  # current included
    #     return [value.getValue() for var, value in self.domains.items()]

    # def undoUpcoming(self):
    #     for i in range(self.ptrToCurr + 1, self.size):
    #         self.domains[i].undoLast(self.changeTags.pop())

    # def anyUpcomingEmpty(self):
    #     for i in range(self.ptrToCurr + 1, self.size):
    #         if self.domains[i].isEmpty():
    #             return True
    #     return False


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
    def __init__(self, variables, domains, constraints):
        self.variables = variables
        self.domains = domains
        self.constraints = constraints
        self.tag = 0

    def backtrackSearch(self):
        return self._try(self.variables, self.domains)

    def _try(self, vars, domains):
        var = vars.getNextVar()
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

    def _fc_check_failed(self, vars, var, domains):
        for value in domains.getDomain(var):
            vars.assignValue(var, value)
            if not self.constraints.areAcceptable(vars.getVarValDict()):
                domains.getDomain(var).removeByVal(value)
        if domains.getDomain(var).isEmpty():
            return True # Domain Wipe Out
        return False

    def forward(self):
        return self._forward(self.variables, self.domains)

    def _forward(self, vars, domains):
        var = vars.getNextVar()
        if var is None:
            return vars.getVarValDict()
        for value in domains.getDomain(var):
            vars.assignValue(var, value)
            if not self.constraints.areAcceptable(vars.getVarValDict()):
                continue
            nextVar = vars.getNextVar()
            if nextVar is None:
                continue
            domainWhipeOutOccured = False
            if self._fc_check_failed(vars,nextVar, domains):
                domainWhipeOutOccured = True
            if not domainWhipeOutOccured:
                return self._forward(vars, domains)
            domains.getDomain(var).restore()
        vars.stepBack()
        return False
