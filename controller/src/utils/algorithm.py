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


def add_green_weights_to_graph(graph):
    
    try:
        north = max(graph.nodes[node]['y'] for node in graph.nodes())
        south = min(graph.nodes[node]['y'] for node in graph.nodes())
        east = max(graph.nodes[node]['x'] for node in graph.nodes())
        west = min(graph.nodes[node]['x'] for node in graph.nodes())
        
        green_areas = ox.features_from_bbox(
            north, south, east, west,
            tags={
                'leisure': ['park', 'garden', 'nature_reserve', 'recreation_ground'],
                'landuse': ['forest', 'grass', 'meadow', 'recreation_ground'],
                'natural': ['wood', 'scrub', 'grassland', 'heath']
            }
        )
        
        log.info(f"Found {len(green_areas)} green areas")
        
        for u, v, key in graph.edges(keys=True):
            node_u = graph.nodes[u]
            node_v = graph.nodes[v]
            edge_lat = (node_u['y'] + node_v['y']) / 2
            edge_lon = (node_u['x'] + node_v['x']) / 2
            
            min_distance_to_green = float('inf')
    
            for idx, green_area in green_areas.iterrows():
                try:
                    if green_area.geometry.geom_type == 'Polygon':
                        from shapely.geometry import Point
                        edge_point = Point(edge_lon, edge_lat)
                        distance = edge_point.distance(green_area.geometry)
                        min_distance_to_green = min(min_distance_to_green, distance)
                    elif green_area.geometry.geom_type == 'MultiPolygon':
                        from shapely.geometry import Point
                        edge_point = Point(edge_lon, edge_lat)
                        for polygon in green_area.geometry.geoms:
                            distance = edge_point.distance(polygon)
                            min_distance_to_green = min(min_distance_to_green, distance)
                except:
                    continue
            
            base_weight = graph[u][v][key]['length']
            
            if min_distance_to_green < 0.001:  
                green_weight = base_weight * 0.3 
                avoid_green_weight = base_weight * 3.0 
            elif min_distance_to_green < 0.005:  
                green_weight = base_weight * 0.6  
                avoid_green_weight = base_weight * 2.0  
            elif min_distance_to_green < 0.01:   
                green_weight = base_weight * 0.8  
                avoid_green_weight = base_weight * 1.5  
            else:
                green_weight = base_weight * 1.2  
                avoid_green_weight = base_weight * 0.8  
            
            graph[u][v][key]['green_weight'] = green_weight
            graph[u][v][key]['avoid_green_weight'] = avoid_green_weight
            
    except Exception as e:
        log.warning(f"Could not load green areas: {e}. Using default weights.")
        for u, v, key in graph.edges(keys=True):
            graph[u][v][key]['green_weight'] = graph[u][v][key]['length']
            graph[u][v][key]['avoid_green_weight'] = graph[u][v][key]['length']


def find_green_route(graph, start_node, end_node, prefer_green=False, avoid_green=False):
    """
    Find route with optional green area preference or avoidance.
    """
    if avoid_green:
        weight_attr = 'avoid_green_weight'
    elif prefer_green:
        weight_attr = 'green_weight'
    else:
        weight_attr = 'length'
    
    try:
        path = nx.shortest_path(graph, start_node, end_node, weight=weight_attr)
        return path
    except nx.NetworkXNoPath:
        if prefer_green or avoid_green:
            log.warning(f"{'Green avoidance' if avoid_green else 'Green preference'} route not found, falling back to regular routing")
            return nx.shortest_path(graph, start_node, end_node, weight='length')
        else:
            raise


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
    
    add_green_weights_to_graph(G)
    
    log.info('Graph loaded')
    _event_graph_loaded.set()


def download_and_save_graph():
    city = "Kraków, Polska"
    G = ox.graph_from_place(city, network_type="walk", simplify=True)
    ox.save_graphml(G, filepath=GRAPH_FILEPATH)
    return G


def find_multiple_green_endpoints(start_lat, start_lon, distance_km, num_attempts=5, avoid_green=False):
    """
    Try multiple directions to find the greenest possible endpoint (or least green if avoiding).
    """
    best_endpoint = None
    best_green_score = float('-inf') if avoid_green else float('inf')
    
    for _ in range(num_attempts):
        random_bearing = random.uniform(0, 360)
        new_lat, new_lon = calculate_new_coords(start_lat, start_lon, distance_km / 2, random_bearing)
        end_node = ox.distance.nearest_nodes(G, new_lon, new_lat)

        green_score = 0
        try:
            neighbors = list(G.neighbors(end_node))[:10]  # Check nearby nodes
            for neighbor in neighbors:
                if G.has_edge(end_node, neighbor):
                    edge_data = G[end_node][neighbor][0]
                    if avoid_green and 'avoid_green_weight' in edge_data:
                        green_score += edge_data['avoid_green_weight'] / edge_data['length']
                    elif not avoid_green and 'green_weight' in edge_data:
                        green_score += edge_data['green_weight'] / edge_data['length']
            
            if avoid_green:
                if green_score < best_green_score or best_green_score == float('-inf'):
                    best_green_score = green_score
                    best_endpoint = (new_lat, new_lon, end_node)
            else:
                if green_score < best_green_score:
                    best_green_score = green_score
                    best_endpoint = (new_lat, new_lon, end_node)
        except:
            continue
    
    return best_endpoint if best_endpoint else (new_lat, new_lon, end_node)


def algorithm(
    starting_point: tuple[float],
    declared_distance: int,
    is_prefer_green: bool = False,
    is_avoid_green: bool = False,
    is_include_weather: bool = False    
):
    global G, _event_graph_loaded

    _event_graph_loaded.wait()
    
    try:
        start_lat, start_lon = starting_point
        distance_km = declared_distance / 1000.0

        start_node = ox.distance.nearest_nodes(G, start_lon, start_lat)
        
        if is_prefer_green or is_avoid_green:
            endpoint_result = find_multiple_green_endpoints(start_lat, start_lon, distance_km, avoid_green=is_avoid_green)
            if len(endpoint_result) == 3:
                new_lat, new_lon, end_node = endpoint_result
            else:
                random_bearing = random.uniform(0, 360)
                new_lat, new_lon = calculate_new_coords(start_lat, start_lon, distance_km / 2, random_bearing)
                end_node = ox.distance.nearest_nodes(G, new_lon, new_lat)
        else:
            random_bearing = random.uniform(0, 360)
            new_lat, new_lon = calculate_new_coords(start_lat, start_lon, distance_km / 2, random_bearing)
            end_node = ox.distance.nearest_nodes(G, new_lon, new_lat)

        path = find_green_route(G, start_node, end_node, is_prefer_green, is_avoid_green)

        half_real_distance = 0
        if is_avoid_green:
            weight_attr = 'avoid_green_weight'
        elif is_prefer_green:
            weight_attr = 'green_weight'
        else:
            weight_attr = 'length'
        
        for i in range(len(path) - 1):
            edge_weight = G[path[i]][path[i+1]][0].get(weight_attr, G[path[i]][path[i+1]][0]['length'])
            half_real_distance += edge_weight
            if half_real_distance >= declared_distance / 2:
                path = path[:i+1]
                break

        path_length = len(path)
        if path_length < 4:
            route_coords = [(G.nodes[node]['x'], G.nodes[node]['y']) for node in path + path[::-1]]
            return route_coords, declared_distance
            
        quarter = path_length // 4
        q1 = path[1:quarter] if quarter > 1 else []
        q2 = path[quarter:2 * quarter] if 2 * quarter > quarter else []
        q3 = path[2 * quarter:3 * quarter] if 3 * quarter > 2 * quarter else []
        q4 = path[3 * quarter:-1] if len(path) > 3 * quarter + 1 else []

        quarters = [q for q in [q1, q2, q3, q4] if len(q) >= 3]

        blocked_nodes = []
        for quarter_path in quarters:
            count = min(random.randint(1, 2), len(quarter_path) - 1)
            selected = select_non_adjacent_nodes(quarter_path, count)
            blocked_nodes.extend(selected)

        G_modified = G.copy()
        G_modified.remove_nodes_from(blocked_nodes)

        try:
            return_path = find_green_route(G_modified, path[-1], start_node, is_prefer_green, is_avoid_green)
        except nx.NetworkXNoPath:
            log.warning("No return path found with blocked nodes, trying with fewer blocks")
            if blocked_nodes:
                G_modified = G.copy()
                G_modified.remove_nodes_from(blocked_nodes[:len(blocked_nodes)//2])
                try:
                    return_path = find_green_route(G_modified, path[-1], start_node, is_prefer_green, is_avoid_green)
                except nx.NetworkXNoPath:
                    return_path = find_green_route(G, path[-1], start_node, is_prefer_green, is_avoid_green)
            else:
                return None, None

        full_path = path + return_path[1:]
        route_coords = [(G.nodes[node]['x'], G.nodes[node]['y']) for node in full_path]

        real_distance = 0
        for i in range(len(path) - 1):
            real_distance += G[path[i]][path[i+1]][0]['length']
        
        graph_for_return = G_modified if path[-1] in G_modified else G
        for i in range(len(return_path) - 1):
            if graph_for_return.has_edge(return_path[i], return_path[i+1]):
                real_distance += graph_for_return[return_path[i]][return_path[i+1]][0]['length']

        route_type = 'green-avoiding' if is_avoid_green else ('green-preferred' if is_prefer_green else 'regular')
        log.info(f"Generated {route_type} route: {len(full_path)} nodes, {int(real_distance)}m")

        return route_coords, int(real_distance)

    except Exception as e:
        log.exception(f"Error in algorithm: {e}")
        return None, 0