#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>


try:
    import gurobipy
except ImportError:
    # for test purposes
    pass

from .solution import Solution
from .config_loader import DEFAULT_CONF

GUROBI_PARAMS = {   
    'TIME_LIMIT': 'TimeLimit',
    'NUM_THREAD': 'Threads',
    'MIN_GAP': 'MIPGap',
}

class Variable:
    def __init__(self, value, selected):
        self.value = value
        self.selected = selected


def create_env(config):
    env = gurobipy.Env()
    env.setParam("OutputFlag", 0)
    
    for k, v in GUROBI_PARAMS.items():
        def_val = DEFAULT_CONF[k]
        conf = config[k]
        if conf != def_val:
            env.setParam(v, conf)

    return env

class Model:

    def __init__(self, mps_file, config, linear_relax=False):
        self.model = gurobipy.read(mps_file, env=create_env(config))
        self.relax = linear_relax
        if linear_relax:
            self.model = self.model.relax()

    def run(self): 
        self.model.optimize()
        return self.model.status == gurobipy.GRB.Status.OPTIMAL

    
    def remove_variable(self, kernel, value=0):
        variables = self.model.getVars()
        for var in filter(lambda x: x not in kernel, variables):
            self.model.addConstr(var == value)

    
    def disable_variables(self, base_kernel, value=0):
        for name, _ in filter(lambda x: not x[1].selected, base_kernel.items()):
            var = self.model.getVarByName(name)
            self.model.addConstr(var == value)
        

    def add_bucket_contraints(self, solution, bucket):
        self.model.addConstr(
            gurobipy.quicksum(self.model.getVarByName(var) for var in bucket) >= 1
        )

        self.model.setParam('Cutoff', solution.value)


    def build_solution(self):
        gen = ((var.varName, var.x) for var in self.model.getVars())
        return Solution(self.model.objVal, gen)
        
    def get_variables(self):
        if self.relax:
            gen = self._lp_variables_()
        else:
            gen = self._int_variables_()
        return dict(gen)

    def _lp_variables_(self):
        for var in self.model.getVars():
            if var.x == 0:
                yield var.varName, Variable(var.rc, False)
            else:
                yield var.varName, Variable(var.x, True)
    
    def _int_variables_(self):
        for var in self.model.getVars():
            yield var.varName, Variable(var.x, True)
