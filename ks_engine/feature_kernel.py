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


def init_feature_kernel(mps_file, config):

    preload_model = Model(mps_file, config, False)
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
        mps_file, config, var_names, model_count, abs_size, min_time, max_time
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

    if search_time_limit:
        config["TIME_LIMIT"] = search_time_limit
    else:
        config.pop("TIME_LIMIT", None)

    return None, kernel, values


def build_kernel_and_values(solution_set, model_size, var_name_table: dict, policy):
    features = compute_feature_importance(solution_set, model_size)

    var_couple = list(zip(var_name_table.keys(), features))
    kernel_size = get_kernel_size(solution_set, policy)

    high_importance_vars = split_kernel_vars(var_couple, kernel_size)

    kernel_vars = build_initial_kernel(var_name_table, high_importance_vars)
    bucket_vars = zip(var_name_table.keys(), features)
    values = Solution(None, bucket_vars)

    return kernel_vars, values


def compute_feature_importance(solution_set, model_size):
    instances, classes = build_sklean_instance(solution_set, model_size)
    classifier = RandomForestClassifier()
    classifier.fit(instances, classes)
    return classifier.feature_importances_


def build_initial_kernel(var_name_table, kernel_var_names):
    for var in kernel_var_names:
        var_name_table[var] = True

    return var_name_table


def generate_model_solutions(
    mps_file, config, var_names, count, size, min_time, max_time
):

    time_limit = min_time
    logger = feature_logger_factory(config["FEATURE_KERNEL"].get("LOG_FILE"))
    solution_set = {}
    for k in range(count):
        print("iter", k)
        if time_limit:
            config["TIME_LIMIT"] = time_limit
        
        selected = generate_random_sub_model(var_names, size)
        result = solve_sub_model(mps_file, config, selected)
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
                if time_limit < max_time:
                    time_limit += 1
                else:
                    size = int(size * 1.1)

        else:
            size *= 2

        if size > len(var_names):
                size = int(len(var_names) * DEF_REL_SIZE)

    logger.save()
    return solution_set


def split_kernel_vars(var_couple, count):
    var_couple.sort(key=lambda x: -x[1])
    head = var_couple[:count]
    kernel = [n for n, i in head]
    return kernel


def build_sklean_instance(solutions, var_count):
    sol_count = len(solutions.values())
    instances = np.ndarray((sol_count, var_count))
    classes = np.ndarray(sol_count)
    for i, value in enumerate(solutions.values()):
        classes[i] = value.status
        instances[i, :] = value.variables.variables()

    return instances, classes


def solve_sub_model(mps_file, config, selected_vars):
    lin_model = Model(mps_file, config, True)
    lin_model.disable_variables(selected_vars)
    stat = lin_model.run()
    if stat:
        base_sol = lin_model.build_solution()
        model = Model(mps_file, config, False, True)
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


def generate_random_sub_model(var_names, count):
    for k in var_names.keys():
        var_names[k] = False

    rng = secrets.SystemRandom()
    
    selected = rng.sample(var_names.keys(), count)
    for sel in selected:
        var_names[sel] = True

    output = {k: None for k, v in var_names.items() if not v}
    return output


def get_variable_name_table(model):
    return {var.varName: False for var in model.model.getVars()}


def cache_solution(curr_sol, cache_file):
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
        output = min((v.model_size for v in vals))


    return output
