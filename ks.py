#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from argparse import ArgumentParser
from ks_engine import *


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("mps", help="Instance MPS file", nargs='?')

    exclusive_group = parser.add_mutually_exclusive_group(required=True)

    exclusive_group.add_argument(
        "-e",
        "--eval",
        default=None,
        help="Evaluate if given solution file is feasible for the given instance",
    )
    exclusive_group.add_argument(
        "-c", "--config", default=None, help="YAML Configuration File"
    )

    return parser.parse_args()

def initialize_algorithm(conf):
    bucket_gen = bucket_builders.get_algorithm(conf["BUCKET"])
    bucket_sort = bucket_sorters.get_algorithm(conf["BUCKET_SORTER"])

    kernel_gen = kernel_builders.get_algorithm(conf["KERNEL"])
    kernel_sort = kernel_sorters.get_algorithm(conf["KERNEL_SORTER"])

    algo = KernelMethods(
        kernel_builder=kernel_gen,
        bucket_builder=bucket_gen,
        bucket_sort=bucket_sort,
        kernel_sort=kernel_sort,
    )
    return algo

def run_kernel_search(mps, config):
    conf = load_config(config)
    mps = get_instance_file(mps, conf)
    
    algo = initialize_algorithm(conf)
    
    sol = kernel_search(mps, conf, algo)
    
    if sol is None:
        print("Cannot find a solution")
    else:
        print("Solution:", sol.value)
        if sol_file := conf["SOLUTION_FILE"]:
            sol.save_as_sol_file(sol_file)
        if debug_file := conf["DEBUG"]:
            sol.debug.export_csv(debug_file, False)


def evaluate_solution(mps, solution):
    if sol := eval_model(mps, solution):
        print(f"Solution file {solution} is a valid solution for {mps}")
        print(f"Objective value: {sol}")
    else:
        print(f"Solution file {solution} is NOT a valid solution for {mps}")


def get_instance_file(mps, config):
    if mps:
        return mps
    elif mps := config.get('INSTANCE'):
        return mps
    else:
        raise ValueError("instance file is required from CLI or from config file")


def solve_instance(args):
    try: 
        run_kernel_search(args.mps, args.config)
    except ValueError as err:
        print("Fatal exception: Value Error")
        print("Error message:", err)
    except RuntimeError as err:
        print("Fatal exception: Runtime Error")
        print("Error message:", err)
    except Exception as err:
        print("Fatal exeption: General Error")
        print("Error message:", err)


def main():
    args = parse_args()
    if args.config is not None:
        solve_instance(args)
    else:
        evaluate_solution(args.mps, args.eval)


if __name__ == "__main__":
    main()
