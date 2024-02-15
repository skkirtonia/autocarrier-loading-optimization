"""
@Author: Sajeeb Kumar Kirtonia
"""
import time
import numpy as np
from ortools.sat.python import cp_model



class LoadingStatesGenerator:
    def __init__(self, am_types: dict, slot_ids: list, constraints: tuple, empty_slot_indicator=0):

        self.am_types = am_types
        self.am_ids = am_types.keys()
        self.slot_ids = slot_ids
        self.single_car, self.double_slot, self.pairwise = constraints
        self.empty_slot_indicator = empty_slot_indicator

        self.solution_time = None
        self.states = None

    def generate(self):
        start_time = time.time_ns()
        # Creates the model.
        model = cp_model.CpModel()
        x = {}
        type_am = {self.am_types[am_id]: [] for am_id in self.am_ids}
        for am_id in self.am_ids:
            type_am[self.am_types[am_id]].append(am_id)

        # Creates the variables.
        for j in self.am_ids:
            x[j] = model.NewIntVar(lb=1, ub=len(self.slot_ids), name=f"x({j})")
        model.AddAllDifferent(x.values())

        # Add single car constraint
        for type, slot in self.single_car:
            if type in type_am.keys():
                for am_id in type_am[type]:
                    model.Add(x[am_id] != slot)

        # Add pairwise constraint
        for t1, s1, t2, s2 in self.pairwise:
            if t1 in type_am.keys() and t2 in type_am.keys():
                for am_id1 in type_am[t1]:
                    for am_id2 in type_am[t2]:
                        b = model.NewBoolVar(f'pair_b_{am_id1}_{s1}_{am_id2}_{s2}')
                        model.Add(x[am_id1] == s1).OnlyEnforceIf(b)
                        model.Add(x[am_id1] != s1).OnlyEnforceIf(b.Not())
                        model.Add(x[am_id2] != s2).OnlyEnforceIf(b)

        # Add double slot constraint
        for t1, s1, s2 in self.double_slot:
            if t1 in type_am.keys():
                for am_id in type_am[t1]:
                    b = model.NewBoolVar(f'double_{am_id}_{s1}_{s2}')
                    model.Add(x[am_id] == s1).OnlyEnforceIf(b)
                    model.Add(x[am_id] != s1).OnlyEnforceIf(b.Not())
                    for other_am in set(self.am_ids) - {am_id}:
                        model.Add(x[other_am] != s2).OnlyEnforceIf(b)

        # Create a solver and solve.
        solver = cp_model.CpSolver()
        solution_printer = self.VarArraySolutionPrinter(x)
        solution_printer.count_slot = len(self.slot_ids)
        solution_printer.empty_slot_indicator = self.empty_slot_indicator

        # Enumerate all solutions.
        solver.parameters.enumerate_all_solutions = True
        # Solve
        solver.Solve(model, solution_printer)
        self.solution_time = (time.time_ns() - start_time) / 1e9
        self.states = solution_printer.states
        return self.states

    class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):

        def __init__(self, variables):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.__variables = variables
            self.__solution_count = 0
            self.states = []

        def on_solution_callback(self):
            self.__solution_count += 1
            state = [self.empty_slot_indicator] * self.count_slot
            for k, v in self.__variables.items():
                state[self.Value(v) - 1] = k
            self.states.append(tuple(state))

        def solution_count(self):
            return self.__solution_count

        def all_solution(self):
            return []



