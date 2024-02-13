def get_sample_constraints():
    # constraint 1
    single_car = [("T1", 2), ("T1", 4), ("T2", 3), ("T2", 5), ("T3", 1), ("T3", 2)]
    double_slot = []
    pairwise = [
        ("T3", 3, "T1", 2), ("T1", 2, "T3", 3),
        ("T3", 2, "T1", 3), ("T1", 3, "T3", 2),
        ("T3", 4, "T2", 3), ("T2", 3, "T3", 4),
        ("T3", 3, "T2", 4), ("T2", 4, "T3", 3),
        ("T3", 4, "T3", 3), ("T3", 3, "T3", 4)
    ]
    return single_car, double_slot, pairwise


def get_constraints_no_constraint():
    # constraint 1
    single_car = []
    double_slot = []
    pairwise = []
    return single_car, double_slot, pairwise


def get_sample_data():
    am_types = {1: "T1", 2: "T2", 3: "T1", 4: "T1"}
    route = [(1, 1), (1, 2), (1, 3), (1, 4), (-1, 1), (-1, 2), (-1, 3), (-1, 4)]
    slot_ids = [1, 2, 3, 4, 5]
    return am_types, route, slot_ids

def get_sample_data2():
    am_types = {1: "T1", 2: "T2"}
    route = [(1, 1), (1, 2), (-1, 1), (-1, 2)]
    slot_ids = [1, 2, 3, 4, 5]
    return am_types, route, slot_ids
