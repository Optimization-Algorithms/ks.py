#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

import math


def fixed_size_bucket(base, values, sorter, sorter_conf, size=1, count=0):
    """
    Build a Generator of bucket of the same dimension.

    :param base: the variables to be inserted in the buckets
    :type base: dict
    :param values: the values to be inserted in the buckets
    :param sorter: a sorting function
    :param sorter_conf: a configuration for the sorter
    :param size: the size of the buckets, defaults to 1
    :type size: int, optional
    :param count: the number of buckets, defaults to 0
    :type count: int, optional
    :raises ValueError: if the number of variables cannot fill the buckets
    :yield: a bucket
    :rtype: list
    """
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
    """
    Build a Generator of bucket of decreasing dimension.

    :param base: the variables to be inserted in the buckets
    :type base: dict
    :param values: the values to be inserted in the buckets
    :param sorter: a sorting function
    :param sorter_conf: a configuration for the sorter
    :param count: the number of buckets, defaults to 0
    :type count: int, optional
    :raises ValueError: if the number of variables cannot fill the buckets
    :yield: a bucket
    :rtype: list
    """
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
