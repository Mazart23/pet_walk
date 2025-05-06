import os
import random
import logging
import threading

import numpy as np
import networkx as nx
import osmnx as ox


G = None
GRAPH_FILEPATH = "/app/graph/cracow_graph.graphml"
_event_graph_loaded = threading.Event()
log = logging.getLogger('ROUTE_ALGORITHM')


def calculate_new_coords(start_lat, start_lon, distance_km, bearing_deg):
    start_lat_rad = np.radians(start_lat)
    start_lon_rad = np.radians(start_lon)
    bearing_rad = np.radians(bearing_deg)
    R = 6371.0

    new_lat_rad = start_lat_rad + (distance_km / R) * np.cos(bearing_rad)
    new_lon_rad = start_lon_rad + (distance_km / R) * np.sin(bearing_rad) / np.cos(start_lat_rad)

    new_lat = np.degrees(new_lat_rad)
    new_lon = np.degrees(new_lon_rad)
    return new_lat, new_lon

def select_non_adjacent_nodes(path_segment, count):
    selected = []
    available_indices = list(range(len(path_segment)))

    while len(selected) < count and available_indices:
        idx = random.choice(available_indices)
        node = path_segment[idx]

        if (idx > 0 and path_segment[idx - 1] in selected) or \
           (idx < len(path_segment) - 1 and path_segment[idx + 1] in selected):
            available_indices.remove(idx)
            continue

        selected.append(node)

        for i in [idx - 1, idx, idx + 1]:
            if i in available_indices:
                available_indices.remove(i)

    return selected

def load_graph():
    log.info('Graph loading started')
    global G, _event_graph_loaded
    if not os.path.exists(GRAPH_FILEPATH):
        G = download_and_save_graph()
    else:
        try:
            G = ox.load_graphml(GRAPH_FILEPATH)
        except Exception as e:
            log.exception(f'Exception during graph loading: {e}')
            G = download_and_save_graph()
    log.info('Graph loaded')
    _event_graph_loaded.set()

def download_and_save_graph():
    city = "Kraków, Polska"
    G = ox.graph_from_place(city, network_type="walk", simplify=True)
    ox.save_graphml(G, filepath=GRAPH_FILEPATH)
    return G

def algorithm(
    starting_point: tuple[float],
    declared_distance: int,
    is_prefer_green: bool = False,
    is_avoid_green: bool = False,
    is_include_wheather: bool = False
):
    global G, _event_graph_loaded

    _event_graph_loaded.wait()
    
    try:
        start_lat, start_lon = starting_point
        distance_km = declared_distance / 1000.0

        random_bearing = random.uniform(0, 360)
        new_lat, new_lon = calculate_new_coords(start_lat, start_lon, distance_km / 2, random_bearing)

        start_node = ox.distance.nearest_nodes(G, start_lon, start_lat)
        end_node = ox.distance.nearest_nodes(G, new_lon, new_lat)

        path = nx.shortest_path(G, start_node, end_node, weight="length")

        half_real_dinstance = 0
        for i in range(len(path) - 1):
            half_real_dinstance += G[path[i]][path[i+1]][0]['length']
            if half_real_dinstance >= distance_km / 2:
                path = path[:i]
                break

        path_length = len(path)
        quarter = path_length // 4
        q1 = path[1:quarter]
        q2 = path[quarter:2 * quarter]
        q3 = path[2 * quarter:3 * quarter]
        q4 = path[3 * quarter:-1]

        quarters = [q1, q2, q3, q4]

        blocked_nodes = []
        for quarter_path in quarters:
            if len(quarter_path) < 3:
                continue
            count = random.randint(2, 3)
            selected = select_non_adjacent_nodes(quarter_path, count)
            blocked_nodes.extend(selected)

        G_modified = G.copy()
        G_modified.remove_nodes_from(blocked_nodes)

        try:
            return_path = nx.shortest_path(G_modified, end_node, start_node, weight="length")
        except nx.NetworkXNoPath:
            return None, None

        route_coords = [(G.nodes[node]['x'], G.nodes[node]['y']) for node in path + return_path]

        real_distance = 0
        for i in range(len(path) - 1):
            real_distance += G[path[i]][path[i+1]][0]['length']
        for i in range(len(return_path) - 1):
            real_distance += G_modified[return_path[i]][return_path[i+1]][0]['length']

        return route_coords, int(real_distance)

    except Exception as e:
        log.exception(f"Error in algorithm: {e}")
        return None, 0
