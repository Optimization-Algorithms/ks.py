#! /usr/bin/python

from .solution import Solution

try:
    import gurobipy
except ImportError:
    print("Gurobi not found: error ignored to allow tests")


def variable_score_factory(sol: Solution, base_kernel: dict, config: dict):
    if config.get("VARIABLE_RANKING"):
        output = VariableRanking(sol, base_kernel)
    else:
        output = ReducedCostScoring(sol, base_kernel)

    return output


class AbstactVariableScoring:
    def __init__(self, solution: Solution, base_kernel: dict):
        self.score = {k: 0 if base_kernel[k] else v for k, v in solution.vars.items()}

    def get_value(self, var_name):
        return self.score[var_name]

    def success_update_score(self, curr_kernel, curr_bucket):
        raise NotImplementedError

    def failure_update_score(self, curr_kernel, curr_bucket):
        raise NotImplementedError



class ReducedCostScoring(AbstactVariableScoring):
    def success_update_score(self, curr_kernel, curr_bucket):
        pass

    def failure_update_score(self, curr_kernel, curr_bucket):
        pass


class VariableRanking(AbstactVariableScoring):
    def cb_update_score(self, name, value):
        if value == 0:
            self.score[name] += 0.1
        else:
            self.score[name] -= 0.1

    def success_update_score(self, curr_kernel, curr_bucket):
        for var in curr_bucket:
            if curr_kernel[var]:
                self.score[var] -= 15
            else:
                self.score[var] += 15

    def failure_update_score(self, curr_kernel, curr_bucket):
        for var in curr_bucket:
            if curr_kernel[var]:
                self.score[var] += 1
            else:
                self.score[var] -= 1



def callback_factory(scoring: AbstactVariableScoring):
    if isinstance(scoring, VariableRanking):
        output = __build_callback__(scoring)
    else:
        output = None

    return output


def __build_callback__(scoring):
    def callback(model, where):
        if where == gurobipy.GRB.Callback.MIPSOL:
            for var in model.getVars():
                value = model.cbGetSolution(var)
                scoring.cb_update_score(var.varName, value)

    return callback
