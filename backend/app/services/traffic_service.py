class TrafficService:
    """
    Conceptual service for traffic flow, congestion analysis, and predictions.
    No simulated traffic or live calculations in Phase 1.
    """

    @staticmethod
    def get_traffic_status(road_id: int):
        raise NotImplementedError("Traffic status calculations are reserved for Phase 2.")

    @staticmethod
    def predict_congestion(road_id: int, time_horizon: int):
        raise NotImplementedError("Traffic predictions are reserved for Phase 2.")
