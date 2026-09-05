from typing import Protocol, List, Any

class VehicleTrackingInterface(Protocol):
    """
    Interface for tracking algorithms (e.g., DeepSORT, ByteTrack).
    """

    def update_tracks(self, detections: List[Any], frame_id: int) -> List[Any]:
        """
        Updates trajectories based on new detections.
        """
        ...
