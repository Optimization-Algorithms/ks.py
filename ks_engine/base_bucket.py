#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>


def get_bucket_variables(kernel: dict):
    tmp = [k for k, v in kernel.items() if v.selected]
    tmp.sort(key=lambda x: kernel[x].value)
    return tmp


def base_bucket_builder(kernel: dict, config):
    variables = get_bucket_variables(kernel)
    length = len(variables)
    size = config["BUCKET_SIZE"]
    start = 0
    while start < length:
        end = start + size
        yield variables[start:end]
        start = end
