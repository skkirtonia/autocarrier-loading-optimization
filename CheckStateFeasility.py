def check_state_feasibility(state, constraints, am_types):
    '''
    Checks if the state is feasible with respect to the constraints.

    :param state: A list of automobile ids where the index of the list is the slot of the auto-carrier.
    For example [0, 1, 2, 3, 0] represents a five slot auto-carrier where 0 represents the empty slots.
    1,2,3 represents the automobile ids which are assigned to various slots.
    Note: slot numbers starts from 1 but in the state the index starts from 0.
    Therefore, automobile in slot s is accessed as state[s-1].

    :param constraints:There are three types of constraints embedded as a tuple in the parameter:
    single_car, double_slot, pairwise = constraints
    single_car: a list of tuples where each item (t, s) indicates that automobiles of type t can not be assigned to slot s.
    double_slot: a list of tuples where each item (t, s1, s2) indicates that automobiles of type t occupies both slot s1 and s2.
    pairwise: a list of tuples where each item (t1, s1, t2, s2) indicates that
    if an automobile of type t1 is assigned to slot s1, another automobile of type t2 can not be assigned to slot s2

    :param am_types: a dictionary mapping automobile id to type of the automobile.

    :return: a boolean indicating whether the state is feasible with respect to the constraints.
    '''

    single_car, double_slot, pairwise = constraints
    # check single_car constraints
    for t, s in single_car:
        if state[s - 1] != 0:
            if am_types[state[s - 1]] == t:
                return False

    # checks double_slot constraint
    for t, s1, s2 in double_slot:
        if state[s1 - 1] != 0 and am_types[state[s1 - 1]] == t:
            if state[s2-1] != 0:
                return False
        if state[s2 - 1] != 0 and am_types[state[s2 - 1]] == t:
            if state[s1-1] != 0:
                return False

    # Checks pairwise constraints
    for t1, s1, t2, s2 in pairwise:
        if state[s1 - 1] != 0 and state[s2 - 1] != 0:
            if am_types[state[s1 - 1]] == t1 and am_types[state[s2 - 1]] == t2:
                return False

    return True
