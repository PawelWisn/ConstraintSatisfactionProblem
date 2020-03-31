from copy import deepcopy


class Variables:
    def __init__(self, arr, ptr=-1):
        self.vars = [x for x in arr]
        self.ptr_to_curr = ptr
        self.size = len(self.vars)

    def get_next_var(self):
        if self.ptr_to_curr == self.size:
            return None
        self.ptr_to_curr += 1
        out = self.vars[self.ptr_to_curr]
        return out

    # def get_prev_var(self):
    #     if self.ptr_to_curr - 1 < 0:
    #         return None
    #     self.ptr_to_curr -= 1
    #     out = self.vars[self.ptr_to_curr]
    #     return out

    def get_by_idx(self, idx):
        self.ptr_to_curr = idx
        return self.vars[idx]

    def get_curr_slice(self):  # current included
        if self.ptr_to_curr >= 0:
            return self.vars[0:self.ptr_to_curr + 1]


class Domain:
    def __init__(self, arr, ptr=-1):
        self.vals = [x for x in arr]
        self.vals_copy = [x for x in arr]
        self.ptr_to_curr = ptr
        self.size = len(arr)

    def reset(self):
        self.vals = [x for x in self.vals_copy]
        self.ptr_to_curr = -1

    def remove_by_idx(self, idx):
        self.vals = self.vals[:idx] + self.vals[idx + 1:]

    def remove_by_val(self, val):
        try:
            self.vals.remove(val)
        except ValueError:
            pass

    # def get_next_val(self):
    #     if self.ptr_to_curr == self.size:
    #         return None
    #     out = self.vals[self.ptr_to_curr]
    #     self.ptr_to_curr += 1
    #     return out

    def get_by_idx(self, idx):
        self.ptr_to_curr = idx
        return self.vals[idx]

    def get_curr_val(self):
        if self.ptr_to_curr>=0:
            return self.vals[self.ptr_to_curr]

    def __iter__(self):
        self.ptr_to_curr = -1
        return self

    def __next__(self):
        if self.ptr_to_curr+1 < self.size:
            self.ptr_to_curr += 1
            return self.vals[self.ptr_to_curr]
        else:
            raise StopIteration


class Domains:
    def __init__(self, arr, ptr=-1):
        self.domains = [Domain(x) for x in arr]
        self.ptr_to_curr = ptr
        self.size = len(self.domains)

    def get_next_dom(self):
        if self.ptr_to_curr == self.size:
            return None
        self.ptr_to_curr += 1
        out = self.domains[self.ptr_to_curr]
        return out

    # def get_prev_dom(self):
    #     if self.ptr_to_curr - 1 < 0:
    #         return None
    #     self.ptr_to_curr -= 1
    #     out = self.domains[self.ptr_to_curr]
    #     return out

    def get_curr_dom(self):
        if self.ptr_to_curr>=0:
            return self.domains[self.ptr_to_curr]

    def get_by_idx(self, idx):
        self.ptr_to_curr = idx
        return self.domains[idx]

    def get_curr_val_slice(self):  # current included
        out = []
        if self.ptr_to_curr>=0:
            for domain in self.domains[0:self.ptr_to_curr +1]:
                out.append(domain.get_curr_val())
            return out


class Constraint:
    def __init__(self, constraint):
        self.constraint = constraint

    def is_satisfied(self, state):
        return self.constraint(state)


class Constraints:
    def __init__(self, arr, ptr=0):
        self.constraints = [Constraint(x) for x in arr]
        self.ptr_to_curr = ptr

    def get_next_con(self):
        if self.ptr_to_curr + 1 >= len(self.constraints):
            self.ptr_to_curr = 0
            return None
        self.ptr_to_curr += 1
        out = self.constraints[self.ptr_to_curr]
        return out

    def are_all_satisfied(self, state):
        for constraint in self.constraints:
            if not constraint.is_satisfied(state):
                return False
        return True


class CSP:
    def __init__(self, variables, domains, constraints, is_complete, state):
        '''
        :param variables: object of Variables class
        :param domains: object of Domains class
        :param constraints: object of Constraints class
        :param is_complete: function that checks if solution is found
        :param state: entry state
        '''
        self.variables = variables
        self.domains = domains
        self.constraints = constraints
        self.is_complete = is_complete
        self.state = state

    def backtrack_search(self):
        return self.try_(self.variables,self.domains, self.state)
        # var_indicator = 0
        # domain_indicator_dict = {}
        # for i in range(len(self.domains)):
        #     domain_indicator_dict[i] = 0
        #
        # while True:
        #     if var_indicator == len(self.variables):  # if there are no variables left
        #         return True  # solution found
        #     else:
        #         var = self.variables[var_indicator]  # take another variable
        #         while True:
        #             if domain_indicator_dict[var_indicator] == len(self.domains[var_indicator]):  # if there are no values left
        #                 self.reset_var(var) # reset changes
        #                 domain_indicator_dict[var_indicator] = 0 # reset domain
        #                 var_indicator -= 1  # go to previous variable
        #                 if var_indicator < 0:  # if there is no previous variable
        #                     return False  # no solution
        #                 else:
        #                     var = self.variables[var_indicator]
        #                     domain_indicator_dict[var_indicator] += 1  # take another value
        #             else:  # if there are values left
        #                 value = self.domains[var_indicator][domain_indicator_dict[var_indicator]]  # take new value
        #                 self.assign_val_to_var(value, var)  # assign it to the variable
        #                 if self.constraints():  # if constraints are satisfied
        #                     var_indicator+=1
        #                     break  # continue with another variable
        #                 else:
        #                     domain_indicator_dict[var_indicator] += 1  # take another value

    def try_(self, vars, doms, state):
        clean_state = deepcopy(state)
        state.update(vars.get_curr_slice(), doms.get_curr_val_slice())
        if self.is_complete(state):
            return doms.get_curr_val_slice(), state
        var = vars.get_next_var()
        for val in doms.get_next_dom():
            # self.assign_val_to_var(val, self.variables[len(prev_vals)])
            state.update([var], [val])
            if self.constraints.are_all_satisfied(state):
                solution = self.try_(deepcopy(vars), deepcopy(doms), clean_state)
                if solution:
                    return solution
        # self.reset_var(self.variables[len(prev_vals)])  #
        # state.print_state()
        return False

    def forward(self, csp):
        pass

    def clear_state(self):
        for var in self.variables:
            self.reset_var(var)

    def constraints(self):
        pass

    def solution_complete(self):
        pass

    def assign_val_to_var(self, val, var):
        pass

    def reset_var(self, var):
        pass
