#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from .model import Model, model_loarder
from .solution import DebugIndex
from .feature_kernel import init_feature_kernel
from collections import namedtuple
import time

KernelMethods = namedtuple(
    "KernelMethods", ["kernel_sort", "kernel_builder", "bucket_sort", "bucket_builder"],
)


def run_solution(model: Model, config):
    """
    Solve the passed model respecting the time limit declared
    in the configuration.

    :param model: the model to solve.
    :type model: Model
    :param config: a configuration to use in the resolution.
    :type config: dict
    :raises RuntimeError: if the solution have timed out.
    :return: True if the solution is optimal, else False.
    :rtype: bool
    """
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
    """
    Initialize a kernel set from the model using a particular configuration.

    :param model: the model to solve.
    :param config: a configuration to use in the resolution.
    :type config: dict
    :param kernel_builder: the kernel builder method to use.
    :type kernel_builder: Callable
    :param kernel_sort: the kernel sorter method to use.
    :type kernel_sort: Callable
    :param mps_file: the name of the file containing the problem.
    :type mps_file: str
    :raises ValueError: if the relaxed problem has no solution.
    :return: the solution value, the initial kernel set and a
        :class:`~ks_engine.solution.Solution`.
    :rtype: tuple
    """
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


def select_vars(base_kernel, bucket):
    """
    Activate all variables inside the bucket,
    so that will be used in the resolution.

    :param base_kernel: a var-isPresentInKernel pair representing
        the kernel set.
    :type base_kernel: dict
    :param bucket: a list of variable, i.e. a bucket.
    """
    for var in bucket:
        base_kernel[var] = True


def update_kernel(base_kernel, bucket, solution, null):
    """
    Remove all null variables inside the bucket from the kernel set.

    :param base_kernel: a var-isPresentInKernel pair representing
        the kernel set.
    :type base_kernel: dict
    :param bucket: a list of variable, i.e. a bucket.
    :param solution: the current solution.
    :param null: a value to consider as the null value, i.e. not assigned.
    """
    for var in bucket:
        if solution.get_value(var) == null:
            base_kernel[var] = False


def run_extension(
    model, config, kernel, bucket, solution, bucket_index, iteration_index
):
    """
    Insert new variables into the kernel set and compute a new solution
    from this one.

    :param model: the model to solve.
    :param config: a configuration to use in the resolution.
    :type config: dict
    :param kernel: a var-isPresentInKernel pair representing
        the kernel set.
    :type kernel: dict
    :param bucket: a list of variable, i.e. a bucket.
    :param solution: the current solution.
    :param bucket_index: the index of the bucket in the bucket list.
    :type bucket_index: int
    :param iteration_index: the cardinal number of the iteration.
    :type iteration_index: int
    :return: a new solution computed using the new kernel set.
    """
    model = Model(model, config)
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


def initialize(model, conf, methods, mps_file):
    """
    Compute an initial kernel set with its attached bucket.

    :param model: the model to solve.
    :param conf: a configuration to use in the resolution.
    :type conf: dict
    :param methods: The collection of four methods:

        * Kernel Builder.
        * Kernel Sorter.
        * Bucket Builder.
        * Bucket Sorter.
    :type methods: namedtuple
    :param mps_file: the name of the file containing the problem.
    :type mps_file: str
    :raises ValueError: if the kernel size raise to the model size.
    :return: the current solution, the kernel set, the list of buckets.
    :rtype: tuple
    """
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
    """
    Detect if the kernel is ill or not.

    An ill kernel is a kernel that is as large as the model, i.e. is the model.

    :param base_kernel: a var-isPresentInKernel pair representing
        the kernel set.
    :type base_kernel: dict
    :return: True if the kernel reached the length of the model, else False.
    :rtype: bool
    """
    kernel_size = sum(1 for v in base_kernel.values() if v)
    model_size = len(base_kernel)
    return kernel_size == model_size


def solve_buckets(model, config, curr_sol, base_kernel, buckets, iteration):
    """
    Pass and solve over all buckets updating the kernel.

    :param model: the model to solve.
    :param config: a configuration to use in the resolution.
    :type config: dict
    :param curr_sol: the current solution that is present before the iteration.
    :param base_kernel: a var-isPresentInKernel pair representing
        the kernel set.
    :type base_kernel: dict
    :param buckets: the list of bucket over which iteration happen.
    :param iteration: the number of the iteration.
    :type iteration: int
    :return: the solution found after iterate over all buckets.
    """
    for index, buck in enumerate(buckets):
        print(index)
        select_vars(base_kernel, buck)
        sol = run_extension(
            model, config, base_kernel, buck, curr_sol, index, iteration
        )
        if sol:
            curr_sol = sol
            update_kernel(base_kernel, buck, curr_sol, 0)
    return curr_sol


def kernel_search(mps_file: str, config, kernel_methods):
    """
    Run Kernel Search Heuristic.

    :param mps_file: The MIP problem instance file.
    :type mps_file: str
    :param config: Kernel Search configuration
    :type config: dict
    :param kernel_methods: The collection of four methods:

        * Kernel Builder.
        * Kernel Sorter.
        * Bucket Builder.
        * Bucket Sorter.
    :type kernel_methods: namedtuple
    :raises ValueError: When the LP relaxation is unsolvable.
        In this case no feasible solution
        are available
    :return: Objective function value
    :rtype: float
    """
    # init_feature_kernel(mps_file, config, None, None)
    # exit()

    main_model = model_loarder(mps_file, config)

    curr_sol, base_kernel, buckets = initialize(main_model, config, kernel_methods, mps_file)
    iters = config["ITERATIONS"]

    if iters > 1:
        buckets = list(buckets)
    prev = curr_sol
    for i in range(iters):
        curr_sol = solve_buckets(main_model, config, curr_sol, base_kernel, buckets, i)
        if curr_sol is None:
            break
        elif prev is None:
            prev = curr_sol
        elif prev.value == curr_sol.value:
            print(f"FIXED POINT FOUND: {prev.value}")
        prev = curr_sol

    return curr_sol
