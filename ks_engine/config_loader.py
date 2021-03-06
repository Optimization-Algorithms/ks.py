#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

import os

from yaml import safe_load


DEFAULT_CONF = {
    "GLOBAL_TIME_LIMIT": -1,
    "TIME_LIMIT": -1,
    "NUM_THREAD": -1,
    "MIP_GAP": 0.0,
    "KERNEL": "base",
    "KERNEL_CONF": {},
    "BUCKET": "fixed",
    "BUCKET_CONF": {"size": 10},
    "PRELOAD": True,
    "LOG": False,
    "KERNEL_SORTER": "base_kernel_sort",
    "KERNEL_SORTER_CONF": {},
    "BUCKET_SORTER": "base_bucket_sort",
    "BUCKET_SORTER_CONF": {},
    "ITERATIONS": 1,
    "PRESOLVE": False,
    "VARIABLE_RANKING": False,
    "INSTANCE": "",
}


def check_config(conf):
    for k, v in DEFAULT_CONF.items():
        c = conf[k]
        if not (type(c) is type(v)):
            raise ValueError(
                f"Configuration Error: {k} should be an {type(v)} found {type(c)} instead"
            )

    if conf["TIME_LIMIT"] > -1 and conf["GLOBAL_TIME_LIMIT"] > -1:
        raise ValueError(
            f"'TIME_LIMIT' and 'GLOBAL_TIME_LIMIT' cannot be set at the same time: only one of them is allowed in a given configuration"
        )

    check_file_parameters(conf)


def get_base_name(instance):
    base_name = os.path.basename(instance)
    index = base_name.rfind(".")
    if index == -1:
        return base_name
    else:
        return base_name[:index]


def check_file_parameters(conf):
    instance = conf.get("INSTANCE")
    if instance:
        base_name = get_base_name(instance)

    if debug := conf.get("DEBUG"):
        if isinstance(debug, bool):
            if instance:
                if debug:
                    conf["DEBUG"] = base_name + "-run.csv"
            else:
                raise ValueError(
                    "cannot set debug file name without an instance name in config file"
                )
        elif not isinstance(debug, str):
            raise ValueError("DEBUG is expected to be a string or boolean")
    else:
        conf["DEBUG"] = None

    if sol := conf.get("SOLUTION_FILE"):
        if isinstance(sol, bool):
            if instance:
                if sol:
                    conf["SOLUTION_FILE"] = base_name + "-sol.sol"
            else:
                raise ValueError(
                    "cannot set solution file name without an instance name in config file"
                )

        elif not isinstance(sol, str):
            raise ValueError("SOLUTION_FILE is expected to be a string or boolean")
    else:
        conf["SOLUTION_FILE"] = None


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
