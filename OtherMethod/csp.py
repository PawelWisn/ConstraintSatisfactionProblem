from copy import deepcopy


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

    # def get_prev_var(self):
    #     if self.ptr_to_curr - 1 < 0:
    #         return None
    #     self.ptr_to_curr -= 1
    #     out = self.vars[self.ptr_to_curr]
    #     return out

    def stepBack(self):
        if self.ptrToCurr >= 0:
            self.ptrToCurr -= 1

    # def getCurrSlice(self):  # current included
    #     if self.ptrToCurr >= 0:
    #         return self.vars[0:self.ptrToCurr + 1]


class Domain:
    def __init__(self, arr, ptr=-1):
        self.vals = [x for x in arr]
        self.valsCopy = [x for x in arr]
        self.ptrToCurr = ptr
        self.size = len(arr)

    def reset(self):
        self.vals = [x for x in self.valsCopy]
        self.size = len(self.vals)
        self.ptrToCurr = -1

    def removeByIdx(self, idx):
        self.vals = self.vals[:idx] + self.vals[idx + 1:]
        self.ptrToCurr = min(self.ptrToCurr, len(self.vals) - 1)
        self.size = len(self.vals)

    def removeByVal(self, val):
        try:
            self.vals.remove(val)
            self.ptrToCurr = min(self.ptrToCurr, len(self.vals) - 1)
            self.size = len(self.vals)
        except ValueError:
            pass

    # def get_next_val(self):
    #     if self.ptr_to_curr == self.size:
    #         return None
    #     out = self.vals[self.ptr_to_curr]
    #     self.ptr_to_curr += 1
    #     return out

    def getByIdx(self, idx):
        self.ptrToCurr = idx
        return self.vals[idx]

    def getCurrVal(self):
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
    def __init__(self, arr, ptr=-1):
        self.domains = [Domain(x) for x in arr]
        self.ptrToCurr = ptr
        self.size = len(self.domains)

    def getNextDom(self):
        if self.ptrToCurr == self.size:
            return None
        self.ptrToCurr += 1
        out = self.domains[self.ptrToCurr]
        return out

    # def get_prev_dom(self):
    #     if self.ptr_to_curr - 1 < 0:
    #         return None
    #     self.ptr_to_curr -= 1
    #     out = self.domains[self.ptr_to_curr]
    #     return out

    def stepBack(self):
        if self.ptrToCurr >= 0:
            self.domains[self.ptrToCurr].reset()
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

    def resetUpcoming(self):
        for i in range(self.ptrToCurr+1,self.size):
            self.domains[i].reset()

    def anyUpcomingEmpty(self):
        for i in range(self.ptrToCurr+1,self.size):
            if self.domains[i].isEmpty():
                return True
        return False


class Constraint:
    def __init__(self, constraint):
        self.constraint = constraint

    def isSatisfied(self, state):
        return self.constraint(state)


class Constraints:
    def __init__(self, arr, ptr=0):
        self.constraints = [Constraint(x) for x in arr]
        self.ptrToCurr = ptr


    def areAllSatisfied(self, state):
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