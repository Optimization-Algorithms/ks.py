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
    """
    Reset the time limit to the default time limit.

    :param config: the actual configuration.
    :type config: dict
    :return: the new value if changed, else None.
    """
    if config["TIME_LIMIT"] != DEFAULT_CONF["TIME_LIMIT"]:
        output = config["TIME_LIMIT"]
        config["TIME_LIMIT"] = DEFAULT_CONF["TIME_LIMIT"]
    else:
        output = None
    return output


def create_env(config):
    """
    Create a gurobi Env and set this with config options.

    :param config: a configuration to set the gurobi Env.
    :type config: dict
    :return: the gurobi env
    """
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
    """
    Load a mps file, and presolve if the config file suggest it.

    :param mps_file: a mps file
    :param config: the configuration for the run.
    :type config: dict
    :return: a model instance.
    """
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
        """
        Preload the solution file from the model if exist.
        """
        if self.sol_file and os.path.isfile(self.sol_file):
            self.model.read(self.sol_file)

    def preload_solution(self, sol=None):
        """
        Preload a solution from local internal variables, if exists.

        :param sol: the current internal solution, defaults to None
        :type sol: [type], optional
        """
        if not self.preload or sol is None:
            return

        for name, value in sol.vars.items():
            self.model.getVarByName(name).start = value

    def run(self):
        """
        Optimize the current model.

        :return: True if it is optimal, else False.
        :rtype: bool
        """
        self.model.optimize()
        stat = self.model.status
        self.stat = stat
        return stat == gurobipy.GRB.status.OPTIMAL

    def disable_variables(self, base_kernel, value=0):
        """
        Disable search over variable that the base_kernel indicate as not in the search space.

        :param base_kernel: a kernel with variables.
        :param value: a value to which set variables to disable, defaults to 0
        :type value: int, optional
        """
        for name, _ in filter(lambda x: not x[1], base_kernel.items()):
            var = self.model.getVarByName(name)
            self.model.addConstr(var == value)

    def add_bucket_contraints(self, solution, bucket):
        """
        Add to a bucket the constraint that the sum of all variables inside the bucket must be >= 1.

        :param solution: a solution for the model.
        :param bucket: the bucket where the constraint must be added.
        """
        self.model.addConstr(
            gurobipy.quicksum(self.model.getVarByName(var) for var in bucket) >= 1
        )
        if solution:
            self.model.setParam("Cutoff", solution.value)

    def build_solution(self, prev_sol=None):
        """
        Build a new solution.

        :param prev_sol: the previous solution, defaults to None
        :return: the best solution between the current and the previous.
        """
        gen = ((var.varName, var.x) for var in self.model.getVars())
        if prev_sol:
            prev_sol.update(self.model.objVal, gen)
        else:
            prev_sol = Solution(self.model.objVal, gen)

        return prev_sol

    def get_base_variables(self, null_value=0.0):
        """
        Returns all variables of the model.

        :param null_value: a value to be considered as the null one, defaults to 0.0
        :type null_value: float, optional
        :return: a dict with all variables name as keys and as value if they are different from the null_value
        :rtype: dict
        """
        gen = ((var.varName, var.x != null_value) for var in self.model.getVars())
        return dict(gen)

    def build_lp_solution(self, null_value=0.0):
        """
        Build the linear programming model.

        Use the current value of the variables if those are not set at the
        null_value, else use the reduced cost.

        :param null_value: a value to be considered as the null one, defaults to 0.0
        :type null_value: float, optional
        :return: a Solution object.
        :rtype: :class:`~ks_engine.solution.Solution`
        """
        gen = self._lp_sol_generator(null_value)
        return Solution(self.model.objVal, gen)

    def _lp_sol_generator(self, null_value):
        for var in self.model.getVars():
            if var.x == null_value:
                yield var.varName, var.rc
            else:
                yield var.varName, var.x

    def build_debug(self, kernel_size, bucket_size):
        """
        Build a :class:`~ks_engine.solution.DebugData` object.

        :param kernel_size: the size of the kernel.
        :type kernel_size: int
        :param bucket_size: the size of the bucket.
        :type bucket_size: int
        :return: a new instance for the debug.
        :rtype: :class:`~ks_engine.solution.DebugData`
        """
        return DebugData(
            value=self.model.objVal,
            time=self.model.getAttr("Runtime"),
            nodes=self.model.getAttr("NodeCount"),
            kernel_size=kernel_size,
            bucket_size=bucket_size,
        )

    def model_size(self):
        """
        Returns the size of the model.

        :return: the size of the, that is the number of variables.
        :rtype: int
        """
        tmp = self.model.getVars()
        output = len(tmp)
        return output

    def reach_solution_limit(self):
        """
        Check if the solution is optimal or reached the setted limit.

        :return: True if one of the two situation is reached, else False.
        :rtype: bool
        """
        time_limit = self.stat == gurobipy.GRB.status.SOLUTION_LIMIT
        optimal = self.stat == gurobipy.GRB.status.OPTIMAL
        return time_limit or optimal

    def reach_time_limit(self):
        """
        Check if the maximum time is elapsed.

        :return: True if the maximum time is elapsed, else False.
        :rtype: bool
        """
        return self.stat == gurobipy.GRB.status.TIME_LIMIT
