#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from .base_kernel import base_kernel_builder

KERNELS = {
    "base": base_kernel_builder,
}

def install_kernel_builder(name, function):
    KERNELS[name] = function

def get_kernel_builder(name):
    return KERNELS[name]
