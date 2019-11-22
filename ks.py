#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from argparse import ArgumentParser
from ks_engine import kernel_search, base_bucket_builder

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('mps', help="Instance MPS file")

    return parser.parse_args()


def main():
    args = parse_args()
    try:
        sol = kernel_search(args.mps, {'BUCKET_SIZE': 10}, base_bucket_builder)
    except ValueError as err:
        print(err)
    else:
        print(sol.value)
        print(sol.vars)


if __name__ == "__main__":
    main()

