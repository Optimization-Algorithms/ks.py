#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from yaml import safe_load


DEFAULT_CONF = {
    "TIME_LIMIT": -1,
    "NUM_THREAD": -1,
    "MIN_GAP": 0.0,
    "KERNEL": "base",
    "BUCKET": "fixed",
    "BUCKET_CONF": {"size": 10},
    "PRELOAD": True,
}


def check_config(conf):
    for k, v in DEFAULT_CONF.items():
        c = conf[k]
        if not (type(c) is type(v)):
            raise ValueError(
                f"Configuration Error: {k} should be an {type(v)} found {type(c)} instead"
            )


def load_config(file_name):
    if not file_name:
        return DEFAULT_CONF

    with open(file_name) as file:
        conf = safe_load(file)

    out = {**DEFAULT_CONF, **conf}
    check_config(out)
    return out
