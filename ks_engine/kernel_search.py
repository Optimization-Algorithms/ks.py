#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>
from collections import namedtuple
import time
from numpy import random

from .model import Model, model_loarder
from .solution import DebugIndex, DebugInfo
from .worsen_score import WorsenScore, MockWorsenScore
from .feature_kernel import init_feature_kernel


KernelMethods = namedtuple(
    "KernelMethods",
    ["kernel_sort", "kernel_builder", "bucket_sort", "bucket_builder"],
)


class KernelSearchInstance:
    def __init__(
        self,
        preload_model,
        kernel_methods,
        kernel,
        buckets,
        current_solution,
        logger,
        config,
        worsen_score,
    ):
        self.preload_model = preload_model
        self.kernel_methods = kernel_methods
        self.kernel = kernel
        self.buckets = buckets
        self.current_solution = current_solution
        self.logger = logger
        self.config = config
        self.worsen_score = worsen_score


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
    instance,
    bucket,
    bucket_index,
    iteration_index,
):
    model = Model(instance.preload_model, instance.config)
    model.disable_variables(instance.kernel)
    prob = instance.worsen_score.get_probability()
    cutoff = random.random() >= prob
    if not cutoff:
        print(
            "Accept worst: ", instance.worsen_score.score, instance.worsen_score.total
        )

    model.add_bucket_contraints(instance.current_solution, bucket, cutoff)
    model.preload_solution(instance.current_solution)

    stat = run_solution(model, instance.config)
    if not stat:
        return None

    solution = model.build_solution(instance.current_solution)
    if instance.config["DEBUG"]:
        debug_index = DebugIndex(iteration_index, bucket_index)
        debug_data = model.build_debug(sum(instance.kernel.values()), len(bucket))
        instance.logger.add_data(debug_data, debug_index)

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


def solve_buckets(instance, iteration):
    local_best = instance.current_solution
    # best_kernel = base_kernel.copy()
    for index, buck in enumerate(instance.buckets):
        select_vars(instance.kernel, buck)
        sol = run_extension(instance, buck, index, iteration)
        print_kernel_size(instance.kernel)
        if sol:
            print(sol.value)
            instance.current_solution = sol
            local_best = get_best_solution(
                instance.current_solution, local_best, instance.preload_model
            )
            if instance.config.get("REMOVE-UNSET"):
                update_kernel(instance.kernel, buck, instance.current_solution, 0)
        else:
            print("No sol")
            #if instance.current_solution:
            #    instance.worsen_score.increase_score()
            allow_kernel_growth = (
                instance.current_solution is None
                and instance.config.get("KERNEL-GROWTH")
            )
            if not allow_kernel_growth:
                unselect_vars(instance.kernel, buck)

    return instance.current_solution, local_best


def get_best_solution(sol_a, sol_b, model):
    if sol_a is None:
        if sol_b is None:
            return None
        return sol_b.copy()
    if sol_b is None:
        return sol_a.copy()

    if model.getAttr("ModelSense") == 1:
        tmp = sol_a if sol_a.value < sol_b.value else sol_b
    else:
        tmp = sol_a if sol_a.value > sol_b.value else sol_b
    return tmp.copy()


def setup_worsen_solution(config):
    if config.get("WORST-SOL"):
        output = WorsenScore(1)
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

    curr_sol, base_kernel, buckets = initialize(
        main_model, config, kernel_methods, mps_file
    )
    iters = config["ITERATIONS"]

    worst_sol = setup_worsen_solution(config)
    if config.get("DEBUG"):
        logger = DebugInfo()
    else:
        logger = None

    best_sol = curr_sol
    prev = curr_sol

    for i in range(iters):
        instance = KernelSearchInstance(
            main_model,
            kernel_methods,
            base_kernel,
            buckets,
            curr_sol,
            logger,
            config,
            worst_sol,
        )
        curr_sol, curr_best = solve_buckets(instance, i)
        best_sol = get_best_solution(curr_best, best_sol, main_model)
        if curr_sol is None:
            break
        if prev is None:
            prev = curr_sol
            instance.worsen_score.increase_total()
        elif prev.value == curr_sol.value:
            worst_sol.increase_score()
            print(f"FIXED POINT FOUND: {prev.value}")
        else:
            instance.worsen_score.increase_total()
            
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
