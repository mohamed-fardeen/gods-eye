from typing import Protocol, List, Any

class IncidentDetectionInterface(Protocol):
    """
    Interface for anomaly detection models (e.g., stationary vehicle, wrong-way driving).
    """

    def detect_anomalies(self, tracking_data: list) -> List[Any]:
        """
        Analyzes recent trajectory data to flag potential incidents.
        """
        ...
