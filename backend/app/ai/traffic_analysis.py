from typing import Protocol, Dict

class TrafficAnalysisInterface(Protocol):
    """
    Interface for predictive models dealing with traffic flow and congestion.
    """

    def predict_congestion(self, historical_data: list, current_state: dict) -> Dict:
        """
        Runs inference to predict near-future congestion levels.
        """
        ...
