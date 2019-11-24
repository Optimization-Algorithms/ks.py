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
    "TIME_LIMIT": "TimeLimit",
    "NUM_THREAD": "Threads",
    "MIN_GAP": "MIPGap",
}


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

        self.preload = config["PRELOAD"]

        self.model = gurobipy.read(mps_file, env=create_env(config))
        self.relax = linear_relax
        if linear_relax:
            self.model = self.model.relax()

    def preload_solution(self, sol):
        if not self.preload:
            return

        for name, value in sol.vars.items():
            self.model.getVarByName(name).start = value

    def run(self):
        self.model.optimize()
        return self.model.status == gurobipy.GRB.Status.OPTIMAL

    def disable_variables(self, base_kernel, value=0):
        for name, _ in filter(lambda x: not x[1], base_kernel.items()):
            var = self.model.getVarByName(name)
            self.model.addConstr(var == value)

    def add_bucket_contraints(self, solution, bucket):
        self.model.addConstr(
            gurobipy.quicksum(self.model.getVarByName(var) for var in bucket) >= 1
        )

        self.model.setParam("Cutoff", solution.value)

    def build_solution(self):
        gen = ((var.varName, var.x) for var in self.model.getVars())
        return Solution(self.model.objVal, gen)

    def get_base_variables(self, null_value=0.0):
        gen = ((var.varName, var.x != null_value) for var in self.model.getVars())
        return dict(gen)

    def build_lp_solution(self, null_value=0.0):
        gen = self._lp_sol_generator(null_value)
        return Solution(self.model.objVal, gen)

    def _lp_sol_generator(self, null_value):
        for var in self.model.getVars():
            if var.x == null_value:
                yield var.varName, var.rc
            else:
                yield var.varName, var.x