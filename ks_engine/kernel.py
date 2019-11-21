#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from collections import namedtuple

Variable = namedtuple('Variable', ['name', 'value', 'selected'])


class Kernel:

    def __init__(self):
        self.store = []

    def get_selected(self):
        for v in self.store:
            if v.selected:
                yield v

    def add_variable(self, name, value):
        tmp = Variable(name, value, True)
        self.store.append(tmp)



    



