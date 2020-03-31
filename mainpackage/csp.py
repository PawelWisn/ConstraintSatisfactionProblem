from abc import ABC, abstractmethod


class Variables:
    def __init__(self, arr, ptr=0):
        self.vars = [x for x in arr]
        self.ptr_to_curr = ptr

    def get_next_var(self):
        if self.ptr_to_curr + 1 >= len(self.vars):
            return None
        self.ptr_to_curr += 1
        out = self.vars[self.ptr_to_curr]
        return out

    def get_prev_var(self):
        if self.ptr_to_curr - 1 < 0:
            return None
        self.ptr_to_curr -= 1
        out = self.vars[self.ptr_to_curr]
        return out


class Domain:
    def __init__(self, arr, ptr=0):
        self.vals = [x for x in arr]
        self.vals_copy = [x for x in arr]
        self.ptr_to_curr = ptr

    def reset(self):
        self.vals = [x for x in self.vals_copy]

    def remove_by_idx(self, idx):
        self.vals = self.vals[:idx] + self.vals[idx + 1:]

    def remove_by_val(self, val):
        try:
            self.vals.remove(val)
        except ValueError:
            pass

    def get_next_val(self):
        if self.ptr_to_curr + 1 >= len(self.vals):
            return None
        self.ptr_to_curr += 1
        out = self.vals[self.ptr_to_curr]
        return out

    def get_prev_val(self):
        if self.ptr_to_curr - 1 < 0:
            return None
        self.ptr_to_curr -= 1
        out = self.vals[self.ptr_to_curr]
        return out

class Domains:
    def __init__(self, arr, ptr=0):
        self.domains = [x for x in arr]
        self.ptr_to_curr = ptr

    def get_next_dom(self):
        if self.ptr_to_curr + 1 >= len(self.domains):
            return None
        self.ptr_to_curr += 1
        out = self.domains[self.ptr_to_curr]
        return out

    def get_prev_dom(self):
        if self.ptr_to_curr - 1 < 0:
            return None
        self.ptr_to_curr -= 1
        out = self.domains[self.ptr_to_curr]
        return out

class CSP(ABC):
    def __init__(self):
        self.variables = []
        self.domains = []

    def backtrack_search(self):
        return self.try_([], self.domains[0])
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

    def try_(self, prev_vals, val_domain):
        self.print_puzzle()
        self.clear_state()
        for var_idx, val in enumerate(prev_vals):
            self.assign_val_to_var(val, self.variables[var_idx])
        if self.solution_complete():
            return prev_vals
        for val in val_domain:
            self.assign_val_to_var(val, self.variables[len(prev_vals)])
            if self.constraints():
                solution = self.try_(prev_vals + [val], self.domains[len(prev_vals)])
                if solution:
                    return solution
        self.reset_var(self.variables[len(prev_vals)])  #
        return False

    def forward(self, csp):
        pass

    def clear_state(self):
        for var in self.variables:
            self.reset_var(var)

    @abstractmethod
    def constraints(self):
        pass

    @abstractmethod
    def solution_complete(self):
        pass

    @abstractmethod
    def assign_val_to_var(self, val, var):
        pass

    @abstractmethod
    def reset_var(self, var):
        pass
