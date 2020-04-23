#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from .model import Model
from .solution import DebugIndex
from collections import namedtuple
import time

KernelMethods = namedtuple(
    "KernelMethods", ["kernel_sort", "kernel_builder", "bucket_sort", "bucket_builder"],
)

def run_solution(model, config):
    begin = time.time_ns()
    stat = model.run()
    end = time.time_ns()
    if config['TIME_LIMIT'] != -1:
        delta = (end - begin) / 1e9 
        delta = int(delta)
        limit = config['TIME_LIMIT']
        limit -= delta
        print("time limit", limit)
        if limit <= 0:
            raise RuntimeError("Time out")
        else:
            config['TIME_LIMIT'] = limit
    return stat

def init_kernel(mps_file, config, kernel_builder, kernel_sort):
    lp_model = Model(mps_file, config, True)
    stat = run_solution(lp_model, config)

    if not stat:
        raise ValueError(f"Given Problem: {mps_file} has no LP solution")

    base = lp_model.get_base_variables()
    values = lp_model.build_lp_solution()
    tmp_sol = lp_model.build_solution()

    kernel = kernel_builder(
        base, values, kernel_sort, config["KERNEL_SORTER_CONF"], **config["KERNEL_CONF"]
    )

    int_model = Model(mps_file, config, False)
    int_model.preload_solution(tmp_sol)
    int_model.disable_variables(kernel)
    stat = run_solution(int_model, config)
    if stat:
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


def run_extension(
    mps_file, config, kernel, bucket, solution, bucket_index, iteration_index
):
    model = Model(mps_file, config)
    model.disable_variables(kernel)
    model.add_bucket_contraints(solution, bucket)
    model.preload_solution(solution)

    stat = run_solution(model, config)
    if not stat:
        return None
    

    solution = model.build_solution(solution)
    if config["DEBUG"]:
        debug_index = DebugIndex(iteration_index, bucket_index)
        debug_data = model.build_debug(sum(kernel.values()), len(bucket))
        solution.update_debug_info(debug_index, debug_data)

    return solution


def initialize(mps_file, conf, methods):
    curr_sol, base_kernel, values = init_kernel(
        mps_file, conf, methods.kernel_builder, methods.kernel_sort
    )

    buckets = methods.bucket_builder(
        base_kernel,
        values,
        methods.bucket_sort,
        conf["BUCKET_SORTER_CONF"],
        **conf["BUCKET_CONF"],
    )
    return curr_sol, base_kernel, buckets


def solve_buckets(mps_file, config, curr_sol, base_kernel, buckets, iteration):
    for index, buck in enumerate(buckets):
        select_vars(base_kernel, buck)
        sol = run_extension(
            mps_file, config, base_kernel, buck, curr_sol, index, iteration
        )
        if sol:
            curr_sol = sol
            update_kernel(base_kernel, buck, curr_sol, 0)
    return curr_sol


def kernel_search(mps_file, config, kernel_methods):
    """
    Run Kernel Search Heuristic

    Parameters
    ----------
    mps_file : str
        The MIP problem instance file.

    config : dict
        Kernel Search configuration

    kernel_methods: KernelMethods
        The collection of four methods:
            - Kernel Builder
            - Kernel Sorter
            - Bucket Builder
            - Bucket Sorter

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
    curr_sol, base_kernel, buckets = initialize(mps_file, config, kernel_methods)
    iters = config["ITERATIONS"]

    if iters > 1:
        buckets = list(buckets)
    prev = None
    for i in range(iters):
        curr_sol = solve_buckets(mps_file, config, curr_sol, base_kernel, buckets, i)
        if curr_sol is None:
            break
        elif prev is None:
            prev = curr_sol
        elif prev.value < curr_sol.value:
            curr_sol = prev
            break

    return curr_sol
