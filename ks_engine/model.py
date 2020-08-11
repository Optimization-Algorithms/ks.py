#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>


try:
    import gurobipy
except ImportError:
    # for test purposes
    pass

from .solution import Solution, DebugData
from .config_loader import DEFAULT_CONF

GUROBI_PARAMS = {
    "TIME_LIMIT": "TimeLimit",
    "NUM_THREAD": "Threads",
    "MIN_GAP": "MIPGap",
}

def create_env(config, one_solution):
    env = gurobipy.Env()
    if not config["LOG"]:
        env.setParam("OutputFlag", 0)

    for k, v in GUROBI_PARAMS.items():
        def_val = DEFAULT_CONF[k]
        conf = config[k]
        if conf != def_val:
            env.setParam(v, conf)

    if one_solution:
        env.setParam("SolutionLimit", 1)


    return env


class Model:
    def __init__(self, mps_file, config, linear_relax=False, one_solution=False):

        self.preload = config["PRELOAD"]
        self.model = gurobipy.read(mps_file, env=create_env(config, one_solution))
        self.relax = linear_relax
        self.stat = None
        if linear_relax:
            self.model = self.model.relax()

    def preload_solution(self, sol=None):
        if not self.preload or sol is None:
            return

        for name, value in sol.vars.items():
            self.model.getVarByName(name).start = value

    def run(self):
        self.model.optimize()
        stat = self.model.status
        self.stat = stat
        return stat == gurobipy.GRB.status.OPTIMAL

    def disable_variables(self, base_kernel, value=0):
        for name, _ in filter(lambda x: not x[1], base_kernel.items()):
            var = self.model.getVarByName(name)
            self.model.addConstr(var == value)

    def add_bucket_contraints(self, solution, bucket):
        self.model.addConstr(
            gurobipy.quicksum(self.model.getVarByName(var) for var in bucket) >= 1
        )
        if solution:
            self.model.setParam("Cutoff", solution.value)

    def build_solution(self, prev_sol=None):
        gen = ((var.varName, var.x) for var in self.model.getVars())
        if prev_sol:
            prev_sol.update(self.model.objVal, gen)
        else:
            prev_sol = Solution(self.model.objVal, gen)

        return prev_sol

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

    def build_debug(self, kernel_size, bucket_size):
        return DebugData(
            value=self.model.objVal,
            time=self.model.getAttr("Runtime"),
            nodes=self.model.getAttr("NodeCount"),
            kernel_size=kernel_size,
            bucket_size=bucket_size,
        )

    def model_size(self):
        tmp = self.model.getVars()
        return len(tmp)


    def reach_solution_limit(self):
        return self.stat == gurobipy.GRB.status.SOLUTION_LIMIT

    def reach_time_limit(self):
        return self.stat == gurobipy.GRB.status.TIME_LIMIT
