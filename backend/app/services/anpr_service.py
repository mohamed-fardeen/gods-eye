class ANPRService:
    """
    Conceptual service for Automatic Number Plate Recognition and OCR.
    No OCR libraries or ML models are loaded in Phase 1.
    """

    @staticmethod
    def identify_plate(image_data: bytes):
        raise NotImplementedError("Number plate detection and OCR are reserved for Phase 2.")
