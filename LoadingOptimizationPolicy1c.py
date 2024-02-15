import time
from matplotlib import pyplot as plt
from CheckStateFeasility import check_state_feasibility
import numpy as np
import networkx as nx
from itertools import permutations


class LoadingOptimizationPolicy1c:
    def __init__(self, route, constraints, am_types, slot_ids, verbose=False):
        """
        :param route: list of (action, automobile id), action = 1 for pickup, action = -1 for drop off for automobile id.
        :param constraints: a tuple (single_car, double_slot, pairwise) that defines all constraints. More details on ChckStateFeasibility.py
        :param am_types: a dictionary mapping automobile id to type of the automobile.
        :param slot_ids: Ids for automobile slots
        :param verbose: True to display intermediate texts.
        """
        # -----------------------------------
        self.route = route
        self.constraints = constraints
        self.am_types = am_types
        self.slot_ids = slot_ids
        self.verbose = verbose
        # -----------------------------------

        self.isFeasible = True
        self.stage_nodes_info = {}
        self.count_slots = len(slot_ids)
        self.solution_loading_plan = None
        self.solution_time = None
        self.solution_count_reloads = None
        self.all_reloads = []
        self.infeasibility_msg = ""

    def run(self):
        time_start = time.time()
        self.solve_with_labeling()
        self.solution_time = time.time() - time_start

    def solve_with_labeling(self):

        start_node = tuple([0] * self.count_slots)
        self.stage_nodes_info[0] = {start_node: {"l": 0, "from": None, "all_from": dict()}}
        if not self.isFeasible:
            return

        for index, (action, vid) in enumerate(self.route):
            if not self.isFeasible:
                break
            prev_labels = self.stage_nodes_info[index]
            current_labels = {}
            for state_prev, node_data_p in prev_labels.items():
                new_state_list = []
                if action == 1:
                    new_state_list = set(self.get_states_adding_new_automobile_ids(state_prev, vid))
                else:
                    new_state_list = set(self.get_states_removing_automobile_ids(state_prev, vid))

                for state_current_new in new_state_list:
                    if check_state_feasibility(state_current_new, self.constraints, self.am_types):
                        # current_labels[state_current_new] = {"l": 1000}
                        if state_current_new in current_labels.keys():
                            count_reload = self.get_count_reload(state_prev, state_current_new)
                            new_label = count_reload + node_data_p["l"]
                            existing_old_node = current_labels[state_current_new]
                            existing_old_node["all_from"] = {**existing_old_node["all_from"], **{state_prev:count_reload}}
                            if new_label < existing_old_node["l"]:

                                current_labels[state_current_new] = {
                                    "l": new_label,
                                    "from": state_prev,
                                    "rc": count_reload,
                                    "all_from": existing_old_node["all_from"]
                                }
                        else:
                            count_reload = self.get_count_reload(state_prev, state_current_new)
                            new_label = count_reload + node_data_p["l"]
                            current_labels[state_current_new] = {
                                "l": new_label,
                                "from": state_prev,
                                "rc": count_reload,
                                "all_from":  {state_prev:count_reload}
                            }



            if len(current_labels.keys()) == 0:
                self.isFeasible = False
                self.infeasibility_msg = f"No feasible state are generated at stop {index + 1, (action, vid)}"
                if self.verbose:
                    print("Infeasible: len(current_labels.keys()) == 0")
                break


            current_labels = {k: v for k, v in current_labels.items() if v["l"] < 1000}
            self.stage_nodes_info[index + 1] = current_labels

            if self.verbose:
                print("Check: len current_labels = ", len(current_labels))

        if self.verbose:
            print("Check: self.isFeasible = ", self.isFeasible)
        if self.isFeasible:
            if self.verbose:
                print("Check: Finding shortest path")

            final_stage_index = len(self.route)
            end_node = tuple([0] * self.count_slots)

            final_stage_labels_dict = self.stage_nodes_info.get(final_stage_index)
            if final_stage_labels_dict is None:
                self.isFeasible = False
                if self.verbose:
                    print("Did not reached to the final stop. Max stop reached = ", max(self.stage_nodes_info.keys()))
            else:
                if end_node in final_stage_labels_dict.keys():
                    self.solution_count_reloads = final_stage_labels_dict[end_node]["l"]

                    plan = [end_node]
                    all_reloads = []
                    current_node = end_node
                    for stage_index in reversed(list(range(1, final_stage_index + 1))):
                        all_reloads.append(self.stage_nodes_info[stage_index][current_node]["l"])
                        from_node = self.stage_nodes_info[stage_index][current_node]["from"]
                        plan.append(from_node)
                        current_node = from_node
                    self.solution_loading_plan = list(reversed(plan))
                    all_reloads.append(self.stage_nodes_info[0][current_node]["l"])
                    all_reloads = np.array(all_reloads[::-1])
                    all_reloads = all_reloads[1:] - all_reloads[:-1]
                    self.all_reloads = all_reloads

                    if self.verbose:
                        print("Reached to the final stop")

    def get_solution(self):

        if self.isFeasible:

            return {
                "is_feasible": self.isFeasible,
                "solution_time": self.solution_time,
                "count_reloads": self.solution_count_reloads,
                "loading_plan": self.solution_loading_plan,
                "all_reloads": self.all_reloads,
                "infeasibility_msg": self.infeasibility_msg,
            }
        else:
            return {
                "is_feasible": self.isFeasible,
                "solution_time": self.solution_time,
                "count_reloads": None,
                "loading_plan": None,
                "all_reloads": None,
                "infeasibility_msg": self.infeasibility_msg,
            }

    def draw(self, hide_links_if_all_connected=False):
        # print(self.stage_nodes_info)
        pos, node_label = self.generate_node_label_and_positions(self.stage_nodes_info)
        G = nx.DiGraph()

        for stage, nodes in self.stage_nodes_info.items():
            if stage > 0:
                for node, node_data in nodes.items():
                    # print(node_data["all_from"])
                    for each_from_node, cost in node_data["all_from"].items():
                        G.add_edge(each_from_node, node_data["node_name"], weight=cost)
                    # G.add_edge(node_data["from"], node_data["node_name"], weight=node_data["rc"])

        plt.figure(figsize=(20, 12))
        top_node_pos_y = max([y for x, y, in pos.values()])
        pos["Route"] = ((1) * 100, top_node_pos_y + 150)
        node_label["Route"] = "Route"
        for i, (action, vid) in enumerate(self.route):
            node_name = f"stop_{i}"
            G.add_node(node_name)
            pos[node_name] = ((i + 2) * 100, top_node_pos_y + 150)
            stop_name = str(vid) + "+" if action == 1 else str(vid) + "-"
            node_label[node_name] = stop_name

        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="white")
        nx.draw_networkx_edges(G, pos, width=.4, arrows=False, alpha=0.8)
        all_edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, alpha=0.8, edge_labels=all_edge_labels)
        nx.draw_networkx_labels(G, pos, labels=node_label)
        if self.solution_loading_plan is not None:
            path_node_names = [str(state).replace(" ", "").replace(",", "")[1:-1] + "-" + str(i) for i, state in enumerate(self.solution_loading_plan)]
            path_edges = list(zip(path_node_names, path_node_names[1:]))
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=2, arrows=False, edge_color="g")
            nx.draw_networkx_edge_labels(G, pos, alpha=0.8, font_color="r", edge_labels={edge: data for edge, data in all_edge_labels.items() if edge in path_edges})
        plt.tight_layout()
        plt.show()
        print("All links are shown with cost.")

    @staticmethod
    def generate_node_label_and_positions(stage_nodes):
        node_position = {}
        node_labels = {}
        for i in range(len(stage_nodes)):
            filtered_nodes = stage_nodes[i]
            y = np.arange(len(filtered_nodes))
            y = y - len(y) // 2
            pos = [((i + 1) * 100, each_y * 150) for each_y in y]
            pos = sorted(pos, key=lambda item: item[1], reverse=True)
            for j, (node, data) in enumerate(sorted(filtered_nodes.items(), key=lambda item: item[1]["l"])):
                node_name = str(node).replace(" ", "").replace(",", "")[1:-1] + "-" + str(i)
                from_node = None
                if data["from"] is not None:
                    from_node = str(data["from"]).replace(" ", "").replace(",", "")[1:-1] + "-" + str(i - 1)

                new_all_from_nodes = dict()
                for each_all_from_node, cost in data["all_from"].items():
                    new_all_from_nodes[str(each_all_from_node).replace(" ", "").replace(",", "")[1:-1] + "-" + str(i - 1)]=cost


                data.update({'node_name': node_name, "from": from_node, "all_from":new_all_from_nodes})
                node_position[node_name] = pos[j]
                node_labels[node_name] = str(node)[1:-1].replace(" ", "").replace(",", "") + f"-{data['l']}"
        return node_position, node_labels

    @staticmethod
    def get_states_adding_new_automobile_ids(state, vid):
        state = list(state)
        for index in range(len(state)):
            new_state = state[:]
            if new_state[index] == 0:
                new_state[index] = vid
                yield tuple(new_state)

    @staticmethod
    def get_states_removing_automobile_ids(state, vid):
        state = list(state)
        for index in range(len(state)):
            new_state = state[:]
            if new_state[index] == vid:
                new_state[index] = 0
                yield tuple(new_state)

    @staticmethod
    def get_count_reload(f_value, t_value):
        # for single level auto-carrier
        f_value = [x for x in list(reversed(f_value)) if x != 0]
        t_value = [x for x in list(reversed(t_value)) if x != 0]
        count_reload = 0
        min_len = min(len(f_value), len(t_value))
        for i in range(min_len):
            if f_value[i] != t_value[i]:
                f1 = set(f_value[i:])
                t1 = set(t_value[i:])
                count_reload = len(f1.intersection(t1))
                break
        return count_reload
