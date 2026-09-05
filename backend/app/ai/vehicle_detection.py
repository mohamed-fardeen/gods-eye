from typing import Protocol, List, Any

class VehicleDetectionInterface(Protocol):
    """
    Interface for future vehicle detection AI models (e.g., YOLO, Faster R-CNN).
    This establishes the contract without implementing PyTorch/TensorFlow logic.
    """

    def load_model(self) -> None:
        """Loads the weights and initializes the model."""
        ...

    def detect_vehicles(self, image_frame: bytes) -> List[Any]:
        """
        Runs inference on an image frame and returns bounding boxes 
        and confidence scores for detected vehicles.
        """
        ...
