#! /usr/bin/python

from collections import namedtuple
import os
import pickle
import secrets

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from .logger import feature_logger_factory
from .model import Model
from .solution import Solution

SubProblem = namedtuple("SubProblem", ["variables", "status", "model_size"])

INFEASIBLE = 0
FEASIBLE = 1
TIME_OUT = 2

DEF_REL_SIZE = 0.01


def init_feature_kernel(model, config):
    """
    Initialize a kernel set from the model using a particular configuration.

    A feature kernel is a particular way to build the kernel that uses some
    particular machine learning technique to try to guess most important
    feature.

    :param model: the model to solve.
    :param config: a configuration to use in the resolution.
    :type config: dict
    :raises ValueError: if no solution is found in the subproblems.
    :return: None, the initial kernel set and a
        :class:`~ks_engine.solution.Solution`.
    :rtype: tuple
    """
    preload_model = Model(model, config, False)
    model_count = config["FEATURE_KERNEL"]["COUNT"]
    abs_size = int(preload_model.model_size() * DEF_REL_SIZE)

    try:
        search_time_limit = config["TIME_LIMIT"]
    except KeyError:
        search_time_limit = None

    try:
        min_time = config["FEATURE_KERNEL"]["MIN_TIME"]
        max_time = config["FEATURE_KERNEL"]["MAX_TIME"]
    except KeyError:
        min_time = None
        max_time = None

    var_names = get_variable_name_table(preload_model)
    solution_set = generate_model_solutions(
        model, config, var_names, model_count, abs_size, min_time, max_time
    )

    if cache_file := config["FEATURE_KERNEL"].get("CACHE_FILE"):
        solution_set = cache_solution(solution_set, cache_file)

    if solution_set:
        kernel, values = build_kernel_and_values(
            solution_set,
            preload_model.model_size(),
            var_names,
            config["FEATURE_KERNEL"].get("POLICY"),
        )
    else:
        raise ValueError(
            f"Unable to find valid subsets in {model_count} iteration, try to increase this number"
        )

    if search_time_limit is not None:
        config["TIME_LIMIT"] = search_time_limit
    else:
        config.pop("TIME_LIMIT", None)

    return None, kernel, values


def build_kernel_and_values(solution_set, model_size, var_name_table: dict, policy):
    """
    Build the kernel set.

    This building is made taking into account the solution_set that are used to
    compute the importance of the features using a machine learning algorithm.

    :param solution_set: a set of different solution
        from different subproblems.
    :type solution_set: dict
    :param model_size: the size of the model.
    :type model_size: int
    :param var_name_table: name-bool pair containing names of vars.
    :type var_name_table: dict
    :param policy: the policy to use to choose the size of the kernel.
    :type policy: str
    :return: a pair of variables in the kernel and a
        :class:`~ks_engine.solution.Solution` with all variables.
    """
    features = compute_feature_importance(solution_set, model_size)

    var_couple = list(zip(var_name_table.keys(), features))
    kernel_size = get_kernel_size(solution_set, policy)

    high_importance_vars = split_kernel_vars(var_couple, kernel_size)

    kernel_vars = build_initial_kernel(var_name_table, high_importance_vars)
    bucket_vars = zip(var_name_table.keys(), features)
    values = Solution(None, bucket_vars)

    return kernel_vars, values


def compute_feature_importance(solution_set, model_size):
    """
    Compute the feature importance, using a random forest.

    :param solution_set: a set of different solution
        from different subproblems.
    :type solution_set: dict
    :param model_size: the size of the model.
    :type model_size: int
    :return: the feature importence for the RF classifier.
    """
    instances, classes = build_sklean_instance(solution_set, model_size)
    classifier = RandomForestClassifier()
    classifier.fit(instances, classes)
    return classifier.feature_importances_


def build_initial_kernel(var_name_table, kernel_var_names):
    """
    Build the initial kernel set.

    :param var_name_table: name-bool pair containing names of vars.
    :type var_name_table: dict
    :param kernel_var_names: names of variable to set in the kernel
    :type kernel_var_names: list
    :return: var_name_table with value True for vars in the kernel.
    :rtype: dict
    """
    for var in kernel_var_names:
        var_name_table[var] = True

    return var_name_table


def generate_model_solutions(
    model, config, var_names, count, size, min_time, max_time
):
    """
    Generate a solution from a model, with respect to other params.

    :param model: the model to solve.
    :param config: a configuration to use in the resolution.
    :type config: dict
    :param var_names: a name-bool pair of all variables.
    :type var_names: dict
    :param count: the number of iteration to execute on the model.
    :type count: int
    :param size: the size of the problem to solve.
    :type size: int
    :param min_time: minimum time to spent in execution.
    :param max_time: maximum time to spent in execution.
    :return: a iter-tuple iteration description pair.
    :rtype: dict
    """
    time_limit = min_time
    logger = feature_logger_factory(config["FEATURE_KERNEL"].get("LOG_FILE"))
    solution_set = {}
    for k in range(count):
        print("iter", k)
        if time_limit:
            config["TIME_LIMIT"] = time_limit

        selected = generate_random_sub_model(var_names, size)
        result = solve_sub_model(model, config, selected)
        logger.log_data(k, size, result)
        if result:
            sol, stat = result

            if stat != TIME_OUT:
                solution_set[k] = SubProblem(sol, stat, size)

            if stat == FEASIBLE:
                size = int(size * 0.9)
            if stat == INFEASIBLE:
                size = int(size * 1.1)
            elif time_limit:
                size = int(size * 0.9)
                if time_limit < max_time:
                    time_limit += 1

        else:
            if time_limit < max_time:
                time_limit += 1
            size = size_grow_function(size, len(var_names))

        if size > len(var_names):
            size = len(var_names)

    logger.save()
    return solution_set


def split_kernel_vars(var_couple, count):
    """
    Split into kernel variables and not.

    :param var_couple: var-value pair.
    :param count: number of variable to put into the kernel.
    :type count: int
    :return: all the variable in the kernel (i.e. count vars).
    :rtype: list
    """
    var_couple.sort(key=lambda x: -x[1])
    head = var_couple[:count]
    kernel = [n for n, i in head]
    return kernel


def build_sklean_instance(solutions, var_count):
    """
    .. warning:: typo in the name. So, not documented now.
    """
    sol_count = len(solutions.values())
    instances = np.ndarray((sol_count, var_count))
    classes = np.ndarray(sol_count)
    for i, value in enumerate(solutions.values()):
        classes[i] = value.status
        instances[i, :] = value.variables.variables()

    return instances, classes


def solve_sub_model(model, config, selected_vars):
    """
    Solve a subproblem with respect to the model
    without the selected vars and the configuration.

    :param model: the supermodel of the model to solve.
    :param config: the configuration for the model.
    :type config: dict
    :param selected_vars: vars to disable.
    :type selected_vars: dict
    :return: if the subproblem has a relaxation a
        tuple with its solution and the status, else None.
    """
    lin_model = Model(model, config, True)
    lin_model.disable_variables(selected_vars)
    stat = lin_model.run()
    if stat:
        base_sol = lin_model.build_solution()
        model = Model(model, config, False, True)
        model.preload_solution(base_sol)
        model.disable_variables(selected_vars)

        model.run()

        if model.reach_solution_limit():
            status = FEASIBLE
        elif model.reach_time_limit():
            status = TIME_OUT
        else:
            status = INFEASIBLE

        return base_sol, status

    return None


def load_model(model, config, relax):
    """
    Create the :class:`~ks_engine.model.Model` according to the config.

    :param model: the model to build as object.
    :param config: the configuration for the model.
    :type config: dict
    :param relax: True if is a relaxation, else False.
    :type relax: bool
    :return: the :class:`~ks_engine.model.Model` object.
    :rtype: :class:`~ks_engine.model.Model`
    """
    if relax:
        output = Model(model, config, True, False)
    else:
        output = Model(model, config, False, True)

    if config["FEATURE_KERNEL"].get("PRELOAD_FILE"):
        output.preload_from_file()

    return output


def generate_random_sub_model(var_names, count):
    """
    Generate randomly a subproblem.

    :param var_names: a name-bool pair.
    :type var_names: dict
    :param count: the number of variables to exclude from the list of vars.
    :type count: int
    :return: a name-None pair representing variables to disable
    :rtype: dict

    .. warning:: The returned variable must be EXCLUDED from the model,
        NOT chosen.
    """
    if count == len(var_names):
        for k in var_names.keys():
            var_names[k] = True
    else:
        var_names = random_select(var_names, count)

    output = {k: None for k, v in var_names.items() if not v}
    return output


def random_select(var_names, count):
    """
    Sample count variable from var_names

    :param var_names: a name-bool pair from which sample.
    :type var_names: dict
    :param count: the number of variables to sample.
    :type count: int
    :return: the variables pair with True if selected, else False.
    :rtype: dict
    """
    for k in var_names.keys():
        var_names[k] = False
    rng = secrets.SystemRandom()

    selected = rng.sample(var_names.keys(), count)

    for sel in selected:
        var_names[sel] = True

    return var_names


def get_variable_name_table(model):
    """
    Compute the list of all names of the variable in the model.

    :param model: the model of which get all the variables names.
    :return: a name-False pair.
    :rtype: dict
    """
    return {var.varName: False for var in model.model.getVars()}


def cache_solution(curr_sol, cache_file):
    """
    Store the current solution to a cache file.

    :param curr_sol: the current solution to store.
    :param cache_file: the cache file name.
    :type cache_file: str
    :return: the current solution with the previous solution values added.
    """
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as file:
            prev_solution = pickle.load(file)
        if curr_sol:
            index = max(curr_sol.keys()) + 1
            for i, val in enumerate(prev_solution.values()):
                curr_sol[index + i] = val
        else:
            curr_sol = prev_solution

    with open(cache_file, "wb") as file:
        pickle.dump(curr_sol, file)

    return curr_sol


def get_kernel_size(solution, policy):
    """
    [Compute the size that the kernel must have with respect to a policy.

    :param solution: a solution from which get the kernel.
    :param policy: the policy to use to choose the size.
    :type policy: str
    :return: the size that the kernel must have.
    :rtype: int
    """
    vals = solution.values()
    infeasible = (v.model_size for v in vals if v.status == INFEASIBLE)
    feasible = (v.model_size for v in vals if v.status == FEASIBLE)
    try:
        if policy == "max-infeasible":
            output = max(infeasible)
        elif policy == "min-infeasible":
            output = min(infeasible)
        elif policy == "max-feasible":
            output = max(feasible)
        else:
            output = min(feasible)
    except ValueError:
        output = min((v.model_size for v in vals if v.status == INFEASIBLE or v.status == FEASIBLE))

    return output


def size_grow_function(curr_size, model_size):
    """
    Compute the new size of the subproblem from the previous.

    :param curr_size: the current size of the model.
    :type curr_size: int
    :param model_size: the model size, that is the upper bound of curr_size.
    :type model_size: int
    :return: the new current size
    :rtype: int
    """
    ratio = curr_size / model_size
    ratio = ratio ** (4 / 5)
    curr_size = int(model_size * ratio)
    return curr_size
