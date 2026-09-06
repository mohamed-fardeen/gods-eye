import socket
try:
    s = socket.create_connection(("127.0.0.1", 8765), 2)
    s.close()
    print("OCR server OK")
except Exception as e:
    print(f"OCR server NOT READY: {e}")
