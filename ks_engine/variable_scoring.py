#! /usr/bin/python

from .solution import Solution

def variable_score_factory(sol: Solution, base_kernel: dict, config: dict):
    if config.get('VARIABLE_RANKING'):
        output = VariableRanking(sol, base_kernel)
    else:
        output = ReducedCostScoring(sol, base_kernel)

    return output

class AbstactVariableScoring:
    def __init__(self, solution: Solution, base_kernel: dict):
        self.score = {k: 0 if base_kernel[k] else v for k, v in solution.vars.items()}

    def get_value(self, var_name):
        return self.score[var_name]


class ReducedCostScoring(AbstactVariableScoring):
    pass


class VariableRanking(AbstactVariableScoring):
    raise NotImplementedError
