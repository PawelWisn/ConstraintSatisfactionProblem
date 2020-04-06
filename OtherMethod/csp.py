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
            return self.vals[self.ptrToCurr]
        else:
            raise StopIteration


class Domains:
    def __init__(self, domains, ptr=-1):
        self.domains = OrderedDict()
        for key, values in domains.items():
            self.domains[key] = Domain(values)
        self.ptrToCurr = ptr
        self.size = len(self.domains)
        self.changeTags = []

    def getNextDom(self):
        if self.ptrToCurr == self.size:
            return None
        self.ptrToCurr += 1
        out = self.domains[self.ptrToCurr]
        return out

    def getDomain(self, var):
        if self.ptrToCurr >= 0:
            return self.domains[var]

    def stepBack(self):
        if self.ptrToCurr >= 0:
            self.domains[self.ptrToCurr].totalReset()
            self.ptrToCurr -= 1

    def getCurrDom(self):
        if self.ptrToCurr >= 0:
            return self.domains[self.ptrToCurr]

    def getByIdx(self, idx):
        self.ptrToCurr = idx
        return self.domains[idx]

    def getValues(self):  # current included
        out = []
        if self.ptrToCurr >= 0:
            for domain in self.domains:
                out.append(domain.getCurrVal())
            return out

    def undoUpcoming(self):
        for i in range(self.ptrToCurr + 1, self.size):
            self.domains[i].undoLast()

    def anyUpcomingEmpty(self):
        for i in range(self.ptrToCurr + 1, self.size):
            if self.domains[i].isEmpty():
                return True
        return False


class Constraints:
    def __init__(self, c, ptr=0):
        self.constraints = c
        self.ptrToCurr = ptr

    def areSatisfied(self, ):
        for constraint in self.constraints:
            if not constraint.isSatisfied(state):
                return False
        return True


class CSP:
    def __init__(self, variables, domains, constraints, state):
        '''
        :param variables: object of Variables class
        :param domains: object of Domains class
        :param constraints: object of Constraints class
        :param state: entry state, need to have an update method
        '''
        self.variables = variables
        self.domains = domains
        self.constraints = constraints
        self.state = state

    def backtrackSearch(self):
        return self.try_(self.variables, self.domains, self.state)

    def try_(self, vars, doms, state):
        var = vars.getNextVar()
        if var is None:
            return doms.getValues(), state
        for val in doms.getNextDom():
            state.update(var, val)
            if self.constraints.areAllSatisfied(state):
                solution = self.try_(vars, doms, state)
                if solution:
                    return solution
            # else:
            # state.downgrade() # not for sudoku

        vars.stepBack()
        doms.stepBack()
        state.downgrade()  # for sudoku
        # state.print_state()
        return False

    def forward(self, vars, doms, state):
        pass
