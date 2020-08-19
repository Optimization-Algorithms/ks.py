#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from yaml import safe_load


DEFAULT_CONF = {
    "TIME_LIMIT": -1,
    "NUM_THREAD": -1,
    "MIN_GAP": 0.0,
    "KERNEL": "base",
    "KERNEL_CONF": {},
    "BUCKET": "fixed",
    "BUCKET_CONF": {"size": 10},
    "PRELOAD": True,
    "LOG": False,
    "DEBUG": '',
    "KERNEL_SORTER": "base_kernel_sort",
    "KERNEL_SORTER_CONF": {},
    "BUCKET_SORTER": "base_bucket_sort",
    "BUCKET_SORTER_CONF": {},
    "ITERATIONS": 1,
}


def check_config(conf):
    for k, v in DEFAULT_CONF.items():
        c = conf[k]
        if not (type(c) is type(v)):
            raise ValueError(
                f"Configuration Error: {k} should be an {type(v)} found {type(c)} instead"
            )


def load_config(file_name):
    """
    Load the configuration from the given file.

    Parameters
    ----------
    file_name : str
        path to the YAML configuration file

    Raises
    ------
    ValueError
        if some variable in the given configuration 
        does not  have the same type of the variables 
        in the default configuration. Other variables 
        are not checked.
    
    Returns
    -------
    config: dict
        map configuration variable name into 
        their values
    """
    if not file_name:
        return DEFAULT_CONF

    with open(file_name) as file:
        conf = safe_load(file)

    out = {**DEFAULT_CONF, **conf}
    check_config(out)
    return out
