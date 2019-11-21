#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from .model import Model

def solve_restricted_mip(mps, config, kernel):
    model = Model(mps_file, config, False)
    model.disable_variables(base_kernel)
    if not model.run():
        raise ValueError(f'Given Problem: {mps_file} has no Initial reduction solution')

    return model.build_solution()


def init_kernel(mps_file, config):
    lp_model = Model(mps_file, config, True)
    if not lp_model.run():
        raise ValueError(f'Given Problem: {mps_file} has no LP solution')
    base_kernel = lp_model.get_variables()
    return solve_restricted_mip(kernel), base_kernel


def select_vars(base_kernel, bucket):
    for var in bucket:
        base_kernel[var].selected = True


def update_kernel(base_kernel, bucket, solution, null):
    for var in bucket:
        if solution.get_value(var) == null:
            base_kernel[var].selected = False


def kernel_search(mps_file, config, bucket_builder):
    curr_sol, base_kernel = init_kernel(mps_file, config)
    buckets = bucket_builder(base_kernel)
    for buck in buckets:
        select_vars(base_kernel, buck)
        sol = solve_restricted_mip(mps_file, config, base_kernel)


    return curr_sol
    