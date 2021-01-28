#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from .model import Model, model_loarder
from .solution import DebugIndex, DebugInfo
from .worsen_score import WorsenScore, MockWorsenScore
from .feature_kernel import init_feature_kernel
from collections import namedtuple
import time
import numpy

KernelMethods = namedtuple(
    "KernelMethods", ["kernel_sort", "kernel_builder", "bucket_sort", "bucket_builder"],
)


def run_solution(model, config):
    begin = time.time_ns()
    stat = model.run()
    end = time.time_ns()
    if config["TIME_LIMIT"] != -1:
        delta = (end - begin) / 1e9
        delta = int(delta)
        limit = config["TIME_LIMIT"]
        limit -= delta
        print("time limit", limit)
        if limit <= 0:
            raise RuntimeError("Time out")
        else:
            config["TIME_LIMIT"] = limit
    return stat


def init_kernel(model, config, kernel_builder, kernel_sort, mps_file):
    lp_model = Model(model, config, True)
    stat = run_solution(lp_model, config)

    if not stat:
        raise ValueError(f"Given Problem: {mps_file} has no LP solution")

    base = lp_model.get_base_variables()
    values = lp_model.build_lp_solution()
    tmp_sol = lp_model.build_solution()

    kernel = kernel_builder(
        base, values, kernel_sort, config["KERNEL_SORTER_CONF"], **config["KERNEL_CONF"]
    )

    int_model = Model(model, config, False)
    if config.get("PRELOAD_FILE"):
        int_model.preload_from_file()
        
    int_model.preload_solution(tmp_sol)
    int_model.disable_variables(kernel)
    stat = run_solution(int_model, config)
    if stat:
        out = int_model.build_solution()
    else:
        out = None

    return out, kernel, values

def add_remove_vars(base_kernel, bucket, add):
    for var in bucket:
        base_kernel[var] = add

def select_vars(base_kernel, bucket):
    add_remove_vars(base_kernel, bucket, True)
    
def unselect_vars(base_kernel, bucket):
    add_remove_vars(base_kernel, bucket, False)


def update_kernel(base_kernel, bucket, solution, null):
    for var in bucket:
        if solution.get_value(var) == null:
            base_kernel[var] = False


def run_extension(
    model, config, kernel, bucket, solution, bucket_index, iteration_index, worst_sol, logger
):
    model = Model(model, config)
    model.disable_variables(kernel)
    prob = worst_sol.get_probability()
    cutoff = numpy.random.random() >= prob
    if not cutoff:
        print("Accept worst: ", worst_sol.score, worst_sol.total)
    model.add_bucket_contraints(solution, bucket, cutoff)
    model.preload_solution(solution)

    stat = run_solution(model, config)
    if not stat:
        return None

    solution = model.build_solution(solution)
    if config["DEBUG"]:
        debug_index = DebugIndex(iteration_index, bucket_index)
        debug_data = model.build_debug(sum(kernel.values()), len(bucket))
        logger.add_data(debug_data, debug_index)

    return solution


def initialize(model, conf, methods, mps_file):
    if conf.get("FEATURE_KERNEL"):
        curr_sol, base_kernel, values = init_feature_kernel(model, conf)
    else:
        curr_sol, base_kernel, values = init_kernel(
            model, conf, methods.kernel_builder, methods.kernel_sort, mps_file
        )

    if ill_kernel(base_kernel):
        raise ValueError("Kernel is large as the whole model")


    buckets = methods.bucket_builder(
        base_kernel,
        values,
        methods.bucket_sort,
        conf["BUCKET_SORTER_CONF"],
        **conf["BUCKET_CONF"],
    )
    
    return curr_sol, base_kernel, buckets

def ill_kernel(base_kernel):
    kernel_size = sum(1 for v in base_kernel.values() if v)
    model_size = len(base_kernel)
    return kernel_size == model_size

def print_kernel_size(kernel):
    count = sum(1 if k else 0 for k in kernel.values())
    print(f"{count}/{len(kernel)}")


def solve_buckets(model, config, curr_sol, base_kernel, buckets, iteration, worst_sol, logger):
    local_best = curr_sol
    #best_kernel = base_kernel.copy()
    for index,  buck in enumerate(buckets):

        select_vars(base_kernel, buck)
        sol = run_extension(
            model, config, base_kernel, buck, curr_sol, index, iteration, worst_sol, logger
        )
        print_kernel_size(base_kernel)
        if sol:
            print(sol.value)
            curr_sol = sol
            worst_sol.increase_total()
            local_best = get_best_solution(curr_sol, local_best, model)
            #update_kernel(base_kernel, buck, curr_sol, 0)
        else:
            print("No sol")
            if curr_sol:
                worst_sol.increase_score()
            unselect_vars(base_kernel, buck)

    return curr_sol, local_best

def get_best_solution(sol_a, sol_b, model):
    if sol_a is None:
        if sol_b is None:
            return None
        else:
            return sol_b.copy()
    elif sol_b is None:
        return sol_a.copy()
            

    if model.getAttr('ModelSense') == 1:
        tmp = sol_a if sol_a.value < sol_b.value else sol_b
    else:
        tmp = sol_a if sol_a.value > sol_b.value else sol_b
    return tmp.copy()

def setup_worsen_solution(config):
    if config.get('WORST-SOL'):
        output = WorsenScore(config['ITERATIONS'])
    else:
        output = MockWorsenScore(0)
    return output

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

    # init_feature_kernel(mps_file, config, None, None)
    # exit()

    main_model = model_loarder(mps_file, config)

    curr_sol, base_kernel, buckets = initialize(main_model, config, kernel_methods, mps_file)
    iters = config["ITERATIONS"]

    worst_sol = setup_worsen_solution(config)
    if config.get("DEBUG"):
        logger = DebugInfo()
    else:
        logger = None

    best_sol = curr_sol
    prev = curr_sol
    for i in range(iters):

        curr_sol, curr_best = solve_buckets(main_model, config, curr_sol, base_kernel, buckets, i, worst_sol, logger)
        best_sol = get_best_solution(curr_best, best_sol, main_model)
        if curr_sol is None:
            break
        elif prev is None:
            prev = curr_sol
        elif prev.value == curr_sol.value:
            worst_sol.increase_score()
            print(f"FIXED POINT FOUND: {prev.value}")

            
        prev = curr_sol
        buckets = kernel_methods.bucket_builder(
            base_kernel,
            curr_sol,
            kernel_methods.bucket_sort,
            config["BUCKET_SORTER_CONF"],
            **config["BUCKET_CONF"],
        )

    if best_sol:
        best_sol.set_debug_info(logger)
    return best_sol
