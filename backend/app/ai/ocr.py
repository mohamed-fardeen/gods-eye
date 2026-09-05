from typing import Protocol

class OCRInterface(Protocol):
    """
    Interface for Optical Character Recognition (e.g. Tesseract, LPRNet).
    """

    def read_text(self, plate_crop: bytes) -> str:
        """
        Extracts the alphanumeric text from a license plate crop.
        """
        ...
