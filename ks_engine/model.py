#! /usr/bin/python

# Copyright (c) 2019 Filippo Ranza <filipporanza@gmail.com>

from collections import namedtuple
import gurobipy
from .solution import Solution



Variable = namedtuple('Variable', ['name', 'value', 'selected'])



class Model:

    def __init__(self, mps_file, config, linear_relax=False):
        self.model = gurobipy.read(mps_file)
        self.relax = linear_relax
        if linear_relax:
            self.model = self.model.relax()

    def run(self): 
        self.model.optimize()
        return self.model.status == gurobipy.GRB.Status.OPTIMAL

    
    def remove_variable(self, kernel, value=0):
        variables = self.model.getVars()
        for var in filter(lambda x: x not in kernel, variables):
            self.model.addConstr(var == value)

    
    def disable_variables(self, base_kernel, value=0):
        for var in filter(lambda var: not var.selected, base_kernel):
            name = self.model.getVarByName(var.name)
            self.model.addConstr(name == value)
        

    def build_solution(self):
        gen = ((var.varName, var.x) for var in self.model.getVars())
        return Solution(self.model.objVal, gen)
        
    def get_variables(self):
        if self.relax:
            gen = self._lp_variables_()
        else:
            gen = self._int_variables_()
        return list(gen)

    def _lp_variables_(self):
        for var in self.model.getVars():
            if var.x == 0:
                yield Variable(var.varName, var.rc, False)
            else:
                yield Variable(var.varName, var.rc, True)
    
    def _int_variables_(self):
        for var in self.model.getVars():
            yield Variable(var.varName, var.x, True)
