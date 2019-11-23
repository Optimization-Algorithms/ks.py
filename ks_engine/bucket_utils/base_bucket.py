#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

import math

def get_bucket_variables(kernel: dict):
    tmp = [k for k, v in kernel.items() if not v.selected]
    tmp.sort(key=lambda x: kernel[x].value)
    return tmp


def fixed_size_bucket(kernel: dict, size):
    variables = get_bucket_variables(kernel)
    length = len(variables)
    start = 0
    while start < length:
        end = start + size
        yield variables[start:end]
        start = end


def decresing_size_bucket(kernel: dict, count):
    
    blocks = sum(1 << i for i in range(count))
    variables = get_bucket_variables(kernel)
    length = len(variables)
    size = math.floor(length / blocks)
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
