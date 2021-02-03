#! /usr/bin/python


from numpy import random as rnd

from .model import Model


class ConstrainManager:
    def __init__(self):
        self.constraints = []
        self.original_constr_count = 0
        self.constraint_count = 0
        self.iis_done = False

    def find_violated_constraint(self, main_model, config, current_kernel):
        if not self.iis_done:
            print("Compute IIS")
            gurobi_model = self.__get_gurobi_model__(main_model, config, current_kernel)
            gurobi_model.computeIIS()
            gurobi_model.update()
            self.__select_random_constraint__(gurobi_model)
            self.iis_done = True
        else:
            print("Using cache")

    def remove_constrains(self, main_model):
        if len(self.constraints):
            print("Run Relaxed model")
        else:
            return main_model

        output = main_model.copy()
        constrs = output.getConstrs()
        self.constraint_count += 1
        rnd.shuffle(self.constraints)
        for index in self.constraints[: self.constraint_count]:
            constr = constrs[index]
            print("Remove constr:", constr)
            output.remove(constr)
            output.update()

        return output

    def clean(self):
        self.constraints = []
        self.constraint_count = 0
        self.original_constr_count = 0
        self.iis_done = False

    def is_accetable_model(self):
        return len(self.constraints) == 0

    def __select_random_constraint__(self, gurobi_model):
        constraints = enumerate(gurobi_model.getConstrs())
        violated_original_constraints = filter(
            lambda constr: constr[1].getAttr("IISConstr")
            and constr[0] < self.original_constr_count,
            constraints,
        )
        constraints_index_list = list(
            map(lambda x: x[0], violated_original_constraints)
        )
        self.constraints = constraints_index_list

    def __get_gurobi_model__(self, main_model, config, current_kernel):
        model = Model(main_model, config)
        self.original_constr_count = len(model.model.getConstrs())
        model.disable_variables(current_kernel)
        gurobi_model = model.model
        gurobi_model.update()
        return gurobi_model
