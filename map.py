"""
    This file contains the Map class that represents an A&A map

    Currently just the North Atlantic though.

    TODO:
        expand map beyond the North Atlantic
"""
import networkx as nx

class Territory:
    def __init__(self, name, ipc_value, is_land, has_ic, is_capital):
        self.name = name
        self.ipc_value = ipc_value
        self.is_land = is_land
        self.has_ic = has_ic
        self.is_capital = is_capital

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class Map:
    def __init__(self, territory_list, adjacency_list):
        self.land = nx.Graph()
        self.sea = nx.Graph()
        self.air = nx.Graph()

        self.territory_map = {
            name : Territory(name, ipc, land, ic, capital) for name, ipc, land, ic, capital in territory_list
        }

        for territory in self.territory_map.values():
            self.air.add_node(territory)
            if territory.is_land:
                self.land.add_node(territory)
            else:
                self.sea.add_node(territory)

        for name1, name2 in adjacency_list:
            t1, t2 = self.territory_map[name1], self.territory_map[name2]
            self.air.add_edge(t1, t2)
            if t1.is_land and t2.is_land:
                self.land.add_edge(t1, t2)
            elif (not t1.is_land) and (not t2.is_land):
                self.sea.add_edge(t1, t2)

SIMPLE_TERRITORY_LIST = [
    # name, ipc value, is_land, has_ic, is_capital
    ("SZ 1", 0, False, False, False),
    ("SZ 2", 0, False, False, False),
    ("SZ 3", 0, False, False, False),
    ("SZ 4", 0, False, False, False),
    ("SZ 5", 0, False, False, False),
    ("SZ 6", 0, False, False, False),
    ("SZ 7", 0, False, False, False),
    ("SZ 8", 0, False, False, False),
    ("SZ 9", 0, False, False, False),
    ("SZ 10", 0, False, False, False),
    ("SZ 11", 0, False, False, False),
    ("SZ 12", 0, False, False, False),
    ("SZ 13", 0, False, False, False),
    ("Eastern Canada", 3, True, False, False),
    ("Eastern United States", 12, True, True, True),
    ("Greenland", 0, True, False, False),
    ("Iceland", 0, True, False, False),
    ("Norway", 2, True, False, False),
    ("Finland", 1, True, False, False),
    ("Karelia", 2, True, True, False),
    ("Baltic States", 2, True, False, False),
    ("Germany", 10, True, True, True),
    ("Northwestern Europe", 2, True, False, False),
    ("France", 6, True, False, False),
    ("United Kingdom", 8, True, True, True),
]

SIMPLE_ADJACENCY = [
    ("SZ 1", "SZ 2"),
    ("SZ 1", "SZ 10"),
    ("SZ 1", "Eastern Canada"),
    ("SZ 2", "Greenland"),
    ("SZ 2", "SZ 3"),
    ("SZ 2", "SZ 7"),
    ("SZ 2", "SZ 9"),
    ("SZ 2", "SZ 10"),
    ("SZ 3", "SZ 4"),
    ("SZ 3", "SZ 6"),
    ("SZ 3", "SZ 7"),
    ("SZ 3", "Iceland"),
    ("SZ 3", "Norway"),
    ("SZ 3", "Finland"),
    ("SZ 4", "Karelia"),
    ("SZ 5", "Norway"),
    ("SZ 5", "Finland"),
    ("SZ 5", "Baltic States"),
    ("SZ 5", "Germany"),
    ("SZ 5", "Northwestern Europe"),
    ("SZ 5", "Karelia"),
    ("SZ 5", "SZ 6"),
    ("SZ 6", "SZ 7"),
    ("SZ 6", "SZ 8"),
    ("SZ 6", "Norway"),
    ("SZ 6", "Northwestern Europe"),
    ("SZ 6", "United Kingdom"),
    ("SZ 7", "SZ 8"),
    ("SZ 7", "SZ 9"),
    ("SZ 7", "United Kingdom"),
    ("SZ 8", "United Kingdom"),
    ("SZ 8", "SZ 9"),
    ("SZ 8", "SZ 13"),
    ("SZ 8", "Northwestern Europe"),
    ("SZ 8", "France"),
    ("SZ 9", "SZ 10"),
    ("SZ 9", "SZ 12"),
    ("SZ 9", "SZ 13"),
    ("SZ 10", "SZ 11"),
    ("SZ 10", "SZ 12"),
    ("SZ 10", "Eastern Canada"),
    ("SZ 11", "SZ 12"),
    ("SZ 11", "Eastern United States"),
    ("SZ 12", "SZ 13"),
    ("Eastern United States", "Eastern Canada"),
    ("Norway", "Finland"),
    ("Finland", "Karelia"),
    ("Karelia", "Baltic States"),
    ("Baltic States", "Germany"),
    ("Germany", "Northwestern Europe"),
    ("Germany", "France"),
    ("Northwestern Europe", "France")
]

def make_simple():
    return Map(SIMPLE_TERRITORY_LIST, SIMPLE_ADJACENCY)


def main():
    map = Map(SIMPLE_TERRITORY_LIST, SIMPLE_ADJACENCY)
    print(map.land_graph)



if __name__ == '__main__':
    main()