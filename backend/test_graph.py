import asyncio
import logging
import sys
from pathlib import Path

# Add backend directory to sys.path so we can import app modules
sys.path.append(str(Path(__file__).parent))

from app.services.transition_graph import graph_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("--- Testing TransitionGraphService ---")
    
    # 1. Load the graph
    # This will download it from OSM on first run, and load from cache subsequently.
    graph_service.load_graph()
    
    if not graph_service.G:
        logger.error("Failed to load graph. Exiting.")
        return
        
    # 2. Define two coordinates in Chennai
    # Camera A: Tidel Park, Taramani
    tidel_lat, tidel_lon = 12.9896, 80.2475
    
    # Camera B: Anna University, Guindy
    anna_lat, anna_lon = 13.0102, 80.2359
    
    logger.info(f"Test Points:")
    logger.info(f"  A (Tidel Park): {tidel_lat}, {tidel_lon}")
    logger.info(f"  B (Anna Univ) : {anna_lat}, {anna_lon}")
    
    # 3. Test Interpolated Path (Ghost inference)
    logger.info("\n--- Testing Ghost Trajectory Inference ---")
    path = graph_service.get_interpolated_path(tidel_lat, tidel_lon, anna_lat, anna_lon)
    logger.info(f"Found path with {len(path)} coordinates.")
    if len(path) > 2:
        logger.info(f"First 3 coords: {path[:3]}")
        logger.info(f"Last 3 coords : {path[-3:]}")
    else:
        logger.info(f"Path: {path}")
        
    # 4. Test Transition Validation (Fuzzy Match validator)
    logger.info("\n--- Testing Spatial-Temporal Validation ---")
    
    # Test 1: Possible transition (15 minutes to travel from Tidel to Anna Univ)
    time_diff_realistic = 15 * 60 # 900 seconds
    is_possible = graph_service.is_transition_possible(tidel_lat, tidel_lon, anna_lat, anna_lon, time_diff_realistic)
    logger.info(f"Is transition possible in 15 mins? {is_possible}")
    
    # Test 2: Impossible transition (30 seconds to travel from Tidel to Anna Univ)
    time_diff_impossible = 30 # 30 seconds
    is_possible = graph_service.is_transition_possible(tidel_lat, tidel_lon, anna_lat, anna_lon, time_diff_impossible)
    logger.info(f"Is transition possible in 30 seconds? {is_possible}")

if __name__ == "__main__":
    asyncio.run(main())
