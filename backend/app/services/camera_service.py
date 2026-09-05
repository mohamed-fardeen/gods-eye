class CameraService:
    """
    Conceptual service for managing CCTV cameras.
    Actual video streaming, CV processing, and live data ingestion will be built here in Phase 2.
    """

    @staticmethod
    def get_camera(camera_id: int):
        raise NotImplementedError("Camera retrieval is reserved for Phase 2.")

    @staticmethod
    def list_cameras():
        raise NotImplementedError("Camera listing is reserved for Phase 2.")

    @staticmethod
    def register_camera(camera_data: dict):
        raise NotImplementedError("Camera registration is reserved for Phase 2.")
