#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

"""
kernel_utils
============

This subpackage servers two main purposes:
    1) contains some basic initial kernel builder
    2) provides a simple selection mechanism to choose between 
    available kernel builders. It is also possibile to add new 
    builders to this list. 
"""


from .select_kernel import get_kernel_builder, install_kernel_builder
