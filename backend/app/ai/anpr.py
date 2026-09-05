from typing import Protocol, List, Any

class ANPRInterface(Protocol):
    """
    Interface for Automatic Number Plate Recognition models.
    """

    def detect_plates(self, image_crop: bytes) -> List[Any]:
        """
        Locates the bounding box of a license plate within a vehicle crop.
        """
        ...
