import os
import networkx as nx
import osmnx as ox
from pathlib import Path
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class TransitionGraphService:
    """
    Singleton service that maintains the spatio-temporal road network graph.
    Uses OSMNx to fetch real-world road data from OpenStreetMap.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TransitionGraphService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        self.G = None
        self.graph_file = Path(__file__).parent.parent.parent / "chennai_network.graphml"
        
        # Center of our mock deployment (Chennai - Guindy area)
        self.center_lat = 13.010236
        self.center_lon = 80.215652
        self.radius_meters = 15000  # 15km radius
        
        self.initialized = True

    def load_graph(self):
        """Loads the graph from cache, or downloads from OSM if missing."""
        try:
            if self.graph_file.exists():
                logger.info(f"Loading cached road network graph from {self.graph_file}...")
                self.G = ox.load_graphml(self.graph_file)
            else:
                logger.info(f"Downloading road network graph for {self.center_lat}, {self.center_lon} (radius {self.radius_meters}m)...")
                # Download driveable road network
                self.G = ox.graph_from_point(
                    (self.center_lat, self.center_lon), 
                    dist=self.radius_meters, 
                    network_type='drive'
                )
                
                # Impute missing edge speeds and calculate travel times
                self.G = ox.add_edge_speeds(self.G)
                self.G = ox.add_edge_travel_times(self.G)
                
                # Save to cache
                logger.info(f"Saving downloaded graph to {self.graph_file}...")
                ox.save_graphml(self.G, self.graph_file)
                
            logger.info(f"Road network graph loaded successfully. Nodes: {len(self.G.nodes)}, Edges: {len(self.G.edges)}")
            
        except Exception as e:
            logger.error(f"Failed to load road network graph: {e}")
            self.G = None

    def get_nearest_node(self, lat: float, lon: float) -> Optional[int]:
        """Snaps a GPS coordinate to the nearest road network node."""
        if not self.G:
            return None
        # osmnx expects (G, Y, X) -> (G, lat, lon)
        return ox.distance.nearest_nodes(self.G, X=lon, Y=lat)

    def get_interpolated_path(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> List[Tuple[float, float]]:
        """
        Calculates the shortest street route between two coordinates.
        Returns a list of [lat, lon] tuples representing the polyline.
        """
        if not self.G:
            # Fallback to straight line if graph fails
            return [[start_lat, start_lon], [end_lat, end_lon]]

        try:
            start_node = self.get_nearest_node(start_lat, start_lon)
            end_node = self.get_nearest_node(end_lat, end_lon)
            
            if start_node == end_node:
                return [[start_lat, start_lon]]
                
            # Calculate shortest path based on travel time
            route = nx.shortest_path(self.G, start_node, end_node, weight='travel_time')
            
            # Extract coordinates for the polyline
            path_coords = []
            
            # Start coordinate (actual camera position)
            path_coords.append([start_lat, start_lon])
            
            # Iterate through the nodes in the route
            for node_id in route:
                node_data = self.G.nodes[node_id]
                # osmnx node data has 'y' (lat) and 'x' (lon)
                path_coords.append([node_data['y'], node_data['x']])
                
            # End coordinate (actual camera position)
            path_coords.append([end_lat, end_lon])
            
            return path_coords
            
        except nx.NetworkXNoPath:
            logger.warning(f"No path found between ({start_lat},{start_lon}) and ({end_lat},{end_lon})")
            return [[start_lat, start_lon], [end_lat, end_lon]]
        except Exception as e:
            logger.error(f"Error calculating path: {e}")
            return [[start_lat, start_lon], [end_lat, end_lon]]

    def is_transition_possible(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float, time_diff_seconds: float) -> bool:
        """
        Validates if a vehicle could physically travel between the two points in the given time.
        Uses the shortest path distance.
        """
        if not self.G or time_diff_seconds <= 0:
            return True # Fail open

        try:
            start_node = self.get_nearest_node(start_lat, start_lon)
            end_node = self.get_nearest_node(end_lat, end_lon)
            
            if start_node == end_node:
                return True
                
            # Calculate shortest distance path (not travel time, we want physical distance)
            distance_meters = nx.shortest_path_length(self.G, start_node, end_node, weight='length')
            
            if distance_meters == 0:
                return True
                
            # Calculate required speed in m/s, then convert to km/h
            speed_mps = distance_meters / time_diff_seconds
            speed_kmh = speed_mps * 3.6
            
            # If the required speed is > 160 km/h in a city, it's physically impossible / highly unlikely
            if speed_kmh > 160.0:
                logger.warning(f"Rejected transition: Required speed is {speed_kmh:.1f} km/h (Dist: {distance_meters}m in {time_diff_seconds}s)")
                return False
                
            return True
            
        except nx.NetworkXNoPath:
            return True # Fail open if no path found
        except Exception as e:
            logger.error(f"Error checking transition possibility: {e}")
            return True # Fail open

# Global instance
graph_service = TransitionGraphService()
