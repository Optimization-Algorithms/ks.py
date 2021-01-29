#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from argparse import ArgumentParser
from ks_engine import *


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("mps", help="Instance MPS file")
    parser.add_argument("-c", "--config", help="YAML Configuration File")

    return parser.parse_args()


def main():
    args = parse_args()
    conf = load_config(args.config)
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
    try:
        sol = kernel_search(args.mps, conf, algo)
    except ValueError as err:
        print(err)
    except RuntimeError as err:
        print(err)
        exit(1)
    else:
        if sol is None:
            print("Cannot find a solution")
        else:
            if sol_file := conf["SOLUTION_FILE"]:
                sol.save_as_sol_file(sol_file)

            print("Solution:", sol.value)
            sol.debug.export_csv(conf["DEBUG"], False)


if __name__ == "__main__":
    main()
