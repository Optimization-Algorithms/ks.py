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
    kernel_gen = kernel_builders.get_algorithm(conf["KERNEL"])
    algo = AlgorithContainer(kernel_builder=kernel_gen, bucket_builder=bucket_gen)
    try:
        sol = kernel_search(args.mps, conf, algo)
    except ValueError as err:
        print(err)
    else:
        print(sol.value)
        # print(sol.vars)


if __name__ == "__main__":
    main()
