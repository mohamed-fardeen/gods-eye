import torch

print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Device name:", torch.cuda.get_device_name(0))
    print("VRAM (GB):", round(torch.cuda.get_device_properties(0).total_memory / 1e9, 2))
    print("CUDA capability:", torch.cuda.get_device_capability(0))
else:
    print("WARNING: No GPU detected. Training will fall back to CPU and be far too")
    print("slow for the 7-8 hour budget. Check drivers / torch CUDA build.")
