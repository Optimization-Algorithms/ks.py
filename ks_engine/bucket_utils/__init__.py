#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

"""
bucket_utils
============

This subpackage servers two main purposes:
    1) contains some basic bucket builder
    2) provides a simple selection mechanism to choose between 
    available bucket builders. It is also possibile to add new 
    builders to this list. 
"""


from .bucket_select import get_bucket, install_bucket_generator
