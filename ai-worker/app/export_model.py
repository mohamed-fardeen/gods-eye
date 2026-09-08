import os
import logging
from ultralytics import YOLO

logger = logging.getLogger(__name__)

def ensure_yolo_onnx(model_name: str = "yolov8n.pt") -> str:
    """
    Ensures that an ONNX version of the YOLO model exists.
    If it doesn't, it loads the .pt model and exports it.
    Returns the path to the .onnx model.
    """
    base_name = os.path.splitext(model_name)[0]
    onnx_path = f"{base_name}.onnx"
    
    if os.path.exists(onnx_path):
        logger.info(f"ONNX model {onnx_path} already exists. Skipping export.")
        return onnx_path
        
    logger.info(f"ONNX model {onnx_path} not found. Exporting {model_name} to ONNX (FP16)...")
    try:
        model = YOLO(model_name)
        # Export with half precision (fp16) to speed up inference and reduce memory
        # dynamic=False is generally faster for fixed-size inputs
        export_path = model.export(format="onnx", half=True, dynamic=False)
        logger.info(f"Successfully exported YOLO model to {export_path}")
        return onnx_path
    except Exception as e:
        logger.error(f"Failed to export YOLO model to ONNX: {e}")
        logger.warning(f"Falling back to standard {model_name}")
        return model_name

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ensure_yolo_onnx("yolov8n.pt")
