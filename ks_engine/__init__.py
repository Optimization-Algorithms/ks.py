#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

"""
ks_engine
=========

An implementation of the Kernel Search Heuristic method

Available functions
-------------------
kernel_search
    run the Kernel Search Heuristic

config_loader
    load ks_engine (and eventually client code) configuration
    from given YAML file



Available subpackages
---------------------
kernel_utils
    contains some basic initial kernel generators 
    and a generator 'factory'

bucket_utils
    contains some basic bucket generators 
    and a generator 'factory'

"""

from .kernel_search import kernel_search, KernelMethods
from .config_loader import load_config
from .kernel_algorithms import *
from .model import eval_model
