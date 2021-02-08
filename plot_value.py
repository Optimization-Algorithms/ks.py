#! /usr/bin/python

from argparse import ArgumentParser

import pandas as pd
from matplotlib import pyplot as plt


def get_values(file):
    csv = pd.read_csv(file)
    values = csv["value"]
    return values.array.to_numpy()


def plot_values(values, log):
    if log:
        plt.semilogy(values)
    else:
        plt.plot(values)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("file", help="ks.py log file")
    parser.add_argument("-l", "--log-scale", default=False, action="store_true")
    parser.add_argument("-o", "--output-file", default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    values = get_values(args.file)
    print("Result:", min(values))
    plot_values(values, args.log_scale)
    if args.output_file:
        plt.savefig(args.output_file)
    else:
        plt.show()


if __name__ == "__main__":
    main()
