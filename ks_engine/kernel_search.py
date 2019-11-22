#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from .model import Model


def init_kernel(mps_file, config):
    lp_model = Model(mps_file, config, True)
    if not lp_model.run():
        raise ValueError(f"Given Problem: {mps_file} has no LP solution")
    base_kernel = lp_model.get_variables()

    int_model = Model(mps_file, config, False)
    int_model.disable_variables(base_kernel)
    if not int_model.run():
        raise ValueError(f"Given Problem: {mps_file} has no Initial reduction solution")

    return int_model.build_solution(), base_kernel


def select_vars(base_kernel, bucket):
    for var in bucket:
        base_kernel[var].selected = True


def update_kernel(base_kernel, bucket, solution, null):
    for var in bucket:
        if solution.get_value(var) == null:
            base_kernel[var].selected = False


def run_extension(mps_file, config, kernel, bucket, solution):
    model = Model(mps_file, config)
    model.disable_variables(kernel)
    model.add_bucket_contraints(solution, bucket)
    if not model.run():
        return None

    return model.build_solution()


def kernel_search(mps_file, config, bucket_builder):
    curr_sol, base_kernel = init_kernel(mps_file, config)
    buckets = bucket_builder(base_kernel, config)
    for buck in buckets:
        select_vars(base_kernel, buck)
        sol = run_extension(mps_file, config, base_kernel, buck, curr_sol)
        if sol:
            curr_sol = sol
        update_kernel(base_kernel, buck, curr_sol, 0)

    return curr_sol
