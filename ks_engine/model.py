#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

import os


try:
    import gurobipy
except ImportError:
    # for test purposes
    pass

from .solution import Solution, DebugData, get_solution_file_name
from .config_loader import DEFAULT_CONF

GUROBI_PARAMS = {
    "TIME_LIMIT": "TimeLimit",
    "NUM_THREAD": "Threads",
    "MIP_GAP": "MIPGap",
}


def reset_time_limit(config):
    if config["TIME_LIMIT"] != DEFAULT_CONF["TIME_LIMIT"]:
        output = config["TIME_LIMIT"]
        config["TIME_LIMIT"] = DEFAULT_CONF["TIME_LIMIT"]
    else:
        output = None
    return output


def create_env(config):
    env = gurobipy.Env()
    if not config["LOG"]:
        env.setParam("OutputFlag", 0)

    for k, v in GUROBI_PARAMS.items():
        def_val = DEFAULT_CONF[k]
        conf = config[k]
        if conf != def_val:
            env.setParam(v, conf)

    return env


def model_loarder(mps_file, config):
    presolve = config["PRESOLVE"]
    if presolve:
        tl = reset_time_limit(config)
        model = gurobipy.read(mps_file, env=create_env(config))
        model.setParam("Presolve", 2)
        model.update()
        output = model.presolve()
        if tl:
            output.setParam("TimeLimit", tl)
        output.setParam("Presolve", -1)
        output.update()
    else:
        output = gurobipy.read(mps_file, env=create_env(config))

    return output


class Model:
    def __init__(self, model, config, linear_relax=False, one_solution=False):

        self.preload = config["PRELOAD"]
        self.sol_file = get_solution_file_name(config.get("SOLUTION_FILE"))
        self.model = model.copy()
        if one_solution:
            self.model.setParam("SolutionLimit", 1)

        self.relax = linear_relax
        self.stat = None
        if linear_relax:
            self.model = self.model.relax()

    def preload_from_file(self):
        if self.sol_file and os.path.isfile(self.sol_file):
            self.model.read(self.sol_file)

    def preload_solution(self, sol=None):
        if not self.preload or sol is None:
            return

        for name, value in sol.vars.items():
            self.model.getVarByName(name).start = value

    def run(self):
        self.model.optimize()
        stat = self.model.status
        self.stat = stat
        obj = self.model.getObjective()
        try:
            obj.getValue()
        except AttributeError:
            output = False
        else:
            output = True

        return output

    def disable_variables(self, base_kernel, value=0):
        for name, _ in filter(lambda x: not x[1], base_kernel.items()):
            var = self.model.getVarByName(name)
            self.model.addConstr(var == value)

    def add_bucket_contraints(self, solution, bucket, cutoff=True):
        self.model.addConstr(
            gurobipy.quicksum(self.model.getVarByName(var) for var in bucket) >= 1
        )
        if solution and cutoff:
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
        output = len(tmp)
        return output

    def reach_solution_limit(self):
        time_limit = self.stat == gurobipy.GRB.status.SOLUTION_LIMIT
        optimal = self.stat == gurobipy.GRB.status.OPTIMAL
        return time_limit or optimal

    def reach_time_limit(self):
        return self.stat == gurobipy.GRB.status.TIME_LIMIT

    def get_status(self):
        status_messages = [
            "LOADED",
            "OPTIMAL",
            "INFEASIBLE",
            "INF_OR_UNBD",
            "UNBOUNDED",
            "CUTOFF",
            "ITERATION_LIMIT",
            "NODE_LIMIT",
            "TIME_LIMIT",
            "SOLUTION_LIMIT",
            "INTERRUPTED",
            "NUMERIC",
            "SUBOPTIMAL",
            "INPROGRESS",
            "USER_OBJ_LIMIT",
        ]
        stat = self.stat - 1
        return status_messages[stat]