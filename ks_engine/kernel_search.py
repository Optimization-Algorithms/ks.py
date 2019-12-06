#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from .model import Model
from collections import namedtuple


KernelMethods = namedtuple(
    "KernelMethods",
    ["kernel_sorter", "kernel_builder", "bucket_sorter", "bucket_builder"],
)


def init_kernel(mps_file, config, kernel_builder, kernel_sort):
    lp_model = Model(mps_file, config, True)
    if not lp_model.run():
        raise ValueError(f"Given Problem: {mps_file} has no LP solution")
    base = lp_model.get_base_variables()
    values = lp_model.build_lp_solution()
    tmp_sol = lp_model.build_solution()

    kernel = kernel_builder(base, values, kernel_sort, config["KERNEL_SORTER_CONF"], **config["KERNEL_CONF"])

    int_model = Model(mps_file, config, False)
    int_model.preload_solution(tmp_sol)
    int_model.disable_variables(kernel)
    if int_model.run():
        out = int_model.build_solution()
    else:
        out = None

    return out, kernel, values


def select_vars(base_kernel, bucket):
    for var in bucket:
        base_kernel[var] = True


def update_kernel(base_kernel, bucket, solution, null):
    for var in bucket:
        if solution.get_value(var) == null:
            base_kernel[var] = False


def run_extension(mps_file, config, kernel, bucket, solution):
    model = Model(mps_file, config)
    model.disable_variables(kernel)
    model.add_bucket_contraints(solution, bucket)
    model.preload_solution(solution)

    if not model.run():
        return None

    return model.build_solution()


def kernel_search(mps_file, config, kernel_methods):
    """
    Run Kernel Search Heuristic

    Parameters
    ----------
    mps_file : str
        The MIP problem instance file.

    config : dict
        Kernel Search configuration

    kernel_builder : callable
        Initial Kernel Generator

    bucket_builder : callable
        Buckets Generator


    Raises
    ------
    ValueError
        When the LP relaxation is unsolvable.
        In this case no feasible solution
        are available

    Returns
    -------
    Value : float
        Objective function value

    Variables: dict 
        Map variable name into its value
        in the solution

    """
    curr_sol, base_kernel, values = init_kernel(
        mps_file, config, kernel_methods.kernel_builder, kernel_methods.kernel_sort
    )

    buckets = kernel_methods.bucket_builder(
        base_kernel, values, kernel_methods.bucket_sort, config["BUCKET_SORTER_CONF"], **config["BUCKET_CONF"]
    )
    for buck in buckets:
        select_vars(base_kernel, buck)
        sol = run_extension(mps_file, config, base_kernel, buck, curr_sol)
        if sol:
            curr_sol = sol
            update_kernel(base_kernel, buck, curr_sol, 0)

    return curr_sol
