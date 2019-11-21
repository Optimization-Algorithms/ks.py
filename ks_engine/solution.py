#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from enum import Enum

class Direction(Enum):
    MINIMIZE = 0
    MAXIMIZE = 1 


class Solution:

    DIRECTION = Direction.MINIMIZE

    def __init__(self, value, var_iter):
        self.vars = {k: v for k, v in var_iter}
        self.value = value

    def better(self, other):
        if Solution.DIRECTION == Direction.MINIMIZE:
            out = self if self.value < other.value else other
        else:
            out = self if self.value > other.value else other
        
        return out