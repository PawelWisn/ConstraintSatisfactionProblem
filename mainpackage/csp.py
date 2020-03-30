from abc import ABC, abstractmethod


class CSP(ABC):
    def __init__(self):
        self.variables = []
        self.domains = []

    def backtrack_search(self):
        var_indicator = 0
        domain_indicator_dict = {}
        for i in range(len(self.domains)):
            domain_indicator_dict[i] = 0

        while True:
            if var_indicator == len(self.variables):  # if there are no variables left
                return True  # solution found
            else:
                var = self.variables[var_indicator]  # take another variable
                while True:
                    if domain_indicator_dict[var_indicator] == len(self.domains[var_indicator]):  # if there are no values left
                        self.reset_var(var) # reset changes
                        domain_indicator_dict[var_indicator] = 0
                        var_indicator -= 1  # go to previous variable
                        if var_indicator < 0:  # if there is no previous variable
                            return False  # no solution
                        else:
                            var = self.variables[var_indicator]
                            domain_indicator_dict[var_indicator] += 1  # take another value
                            continue
                    else:  # if there are values left
                        value = self.domains[var_indicator][domain_indicator_dict[var_indicator]]  # take new value
                        self.assign_val_to_var(value, var)  # assign it to the variable
                        if self.constraints():  # if constraints are satisfied
                            var_indicator+=1
                            break  # continue with another variable
                        else:
                            domain_indicator_dict[var_indicator] += 1  # take another value
                            continue

    def forward(self, csp):
        pass

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