#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

import math


def fixed_size_bucket(base, values, sorter, sorter_conf, size=1, count=0):
    variables = sorter(base, values, **sorter_conf)
    length = len(variables)
    if count:
        size = length // count
    if size == 0:
        raise ValueError(f"Variable outside kernel [{length}] are not enough for {count} buckets")

    start = 0
    while start < length:
        end = start + size
        yield variables[start:end]
        start = end


def decresing_size_bucket(base, values, sorter, sorter_conf, count):
    variables = sorter(base, values, **sorter_conf)
    blocks = sum(1 << i for i in range(count))
    length = len(variables)
    size = math.floor(length / blocks)
    if size == 0:
        raise ValueError(f"Variable outside kernel [{length}] are not enough for {count} buckets")

    start = 0
    blocks = 1 << (count - 1)
    while start < length:

        if blocks:
            end = start + (blocks * size)
        else:
            end = length

        yield variables[start:end]
        start = end
        blocks >>= 1


BUCKET_BUILDERS = {"fixed": fixed_size_bucket, "decrease": decresing_size_bucket}
