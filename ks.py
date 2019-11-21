#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from argparse import ArgumentParser
from ks_engine import kernel_search

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('mps', help="Instance MPS file")

    return parser.parse_args()


def main():
    args = parse_args()
    sol = kernel_search(args.mps, None)
    print(sol.value)
    print(sol.vars)


if __name__ == "__main__":
    main()

