#! /usr/bin/python

from collections import namedtuple
import os
import pickle

import numpy as np
from sklearn.ensemble import RandomForestClassifier

import secrets

from .model import Model

SubProblem = namedtuple("SubProblem", ["variables", "status", "model_size"])

INFEASIBLE = 0
FEASIBLE = 1
TIME_OUT = 2

DEF_REL_SIZE = 0.01


def init_feature_kernel(mps_file, config, kernel_builder, kernel_sort):

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

    var_names = get_var_table(preload_model)
    solution_set = generate_model_solutions(
        mps_file, config, var_names, model_count, abs_size, min_time, max_time
    )

    if cache_file := config["FEATURE_KERNEL"]["CACHE_FILE"]:
        solution_set = cache_solution(solution_set, cache_file)

    if len(solution_set):
        instances, classes = convert_solutions(solution_set, preload_model.model_size())
        classifier = RandomForestClassifier()
        classifier.fit(instances, classes)
        features = classifier.feature_importances_
        var_couple = couple_variables(get_var_name(preload_model), features)
        kernel_size = get_kernel_size(solution_set, config["FEATURE_KERNEL"].get('POLICY'))
        kernel = find_most_important(var_couple, kernel_size)
        print(kernel)
    else:
        raise ValueError(
            f"Unable to find valid subsets in {model_count} iteration, try to increase this number"
        )

    if search_time_limit:
        config["TIME_LIMIT"] = search_time_limit
    else:
        config.pop("TIME_LIMIT", None)

    # groups = build_groups(get_var_names(preload_model), group_count)


def generate_model_solutions(
    mps_file, config, var_names, count, size, min_time, max_time
):

    time_limit = min_time

    solution_set = {}
    for k in range(count):
        print("iter", k)
        if time_limit:
            config["TIME_LIMIT"] = time_limit

        selected = select_random_vars(var_names, size)
        result = solve_model(mps_file, config, selected)

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

            if size > len(var_names):
                size = int(len(var_names) * DEF_REL_SIZE)

        else:
            size *= 2

    return solution_set


def couple_variables(var_names, feature_importance):
    return [(n, i) for n, i in zip(var_names, feature_importance)]


def find_most_important(var_couple, count):
    var_couple.sort(key=lambda x: -x[1])
    head = var_couple[:count]
    return [n for n, i in head]


def convert_solutions(solutions, var_count):
    sol_count = len(solutions.values())
    instances = np.ndarray((sol_count, var_count))
    classes = np.ndarray(sol_count)
    for i, v in enumerate(solutions.values()):
        classes[i] = v.status
        instances[i, :] = v.variables.variables()

    return instances, classes


def solve_model(mps_file, config, selected_vars):
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

    else:
        return None


def select_random_vars(var_names, count):
    for k in var_names.keys():
        var_names[k] = False

    rng = secrets.SystemRandom()
    selected = rng.sample(var_names.keys(), count)
    for sel in selected:
        var_names[sel] = True

    output = {k: None for k, v in var_names.items() if not v}
    return output


def build_groups(var_names, groups):
    var_count = len(var_names)
    group_size = len(var_names) // groups
    if var_count % groups:
        group_size += 1
    begin = 0
    output = [None] * groups
    for i in range(groups):
        output[i] = var_names[begin : begin + group_size]
        begin += group_size

    return output


def get_var_table(model):
    return {var.varName: False for var in model.model.getVars()}


def get_var_name(model):
    return [var.varName for var in model.model.getVars()]


def cache_solution(curr_sol, cache_file):
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as file:
            prev_solution = pickle.load(file)
        if curr_sol:
            index = max(curr_sol.keys()) + 1
            for i, v in enumerate(prev_solution.values()):
                curr_sol[index + i] = v
        else:
            curr_sol = prev_solution

    with open(cache_file, "wb") as file:
        pickle.dump(curr_sol, file)

    return curr_sol



def get_kernel_size(solution, policy):
    vals = solution.values()
    infeasible = (v.model_size for v in vals if v.status == INFEASIBLE)
    feasible = (v.model_size for v in vals if v.status == FEASIBLE)
    if policy == 'max-infeasible':
        output = max(infeasible)
    elif policy == 'min-infeasible':
        output = min(infeasible)
    elif policy == 'max-feasible':
        output = max(feasible)
    else:
        output = min(feasible)

    return output


