#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>


import math

def base_kernel_builder(base, values):
    return base


def sort_base_variables(base, values):
    kernel = [name for name, select in base.items() if select]
    kernel.sort(key=lambda x: values.get_value(x))
    return kernel

def percentage_better_kernel_builder(base, value, percentage):
    kernel_vars = sort_base_variables(base, value)
    last_taken = math.floor(len(kernel_vars) * percentage)
    for name in kernel_vars[last_taken:]:
        base[name] = False
    return base



