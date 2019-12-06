#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>


class Solution:
    def __init__(self, value, var_iter):
        self.vars = {k: v for k, v in var_iter}
        self.value = value

    def get_value(self, name):
        return self.vars[name]

    def update(self, value, var_iter):
        self.value = value
        for k, v in var_iter:
            self.vars[k] = v
