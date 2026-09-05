class DetectionService:
    """
    Conceptual boundary for YOLO/TensorFlow detection models.
    No image processing or models are loaded in Phase 1.
    """

    @staticmethod
    def process_frame(camera_id: int, frame_data: bytes):
        raise NotImplementedError("Frame processing and CV models are reserved for Phase 2.")

    @staticmethod
    def get_recent_detections(camera_id: int):
        raise NotImplementedError("Detection retrieval is reserved for Phase 2.")
