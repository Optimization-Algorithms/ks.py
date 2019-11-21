#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from yaml import safe_load

DEFAULT_CONF = {    
    'TIME_LIMIT': -1,
    'NUM_THREAD': -1, 
}


def load_config(file_name):
    with open(file_name) as file:
        conf = safe_load(file)

    out = {**conf, **DEFAULT_CONF}
    return conf



