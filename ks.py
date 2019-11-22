#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from argparse import ArgumentParser
from ks_engine import *

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('mps', help="Instance MPS file")
    parser.add_argument('-c', '--config', help="YAML Configuration File")

    return parser.parse_args()


def main():
    args = parse_args()
    conf = load_config(args.config)
    try:
        sol = kernel_search(args.mps, conf, base_bucket_builder)
    except ValueError as err:
        print(err)
    else:
        print(sol.value)
        print(sol.vars)


if __name__ == "__main__":
    main()

