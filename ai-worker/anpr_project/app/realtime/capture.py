import time
import threading
import cv2

class LiveCapture:
    """
    True Low-Latency Latest-Frame Live Capture.
    Maintains exactly ONE decoded frame slot.
    Aggressively drops stale frames when inference is slower than the source.
    Implements grab()/retrieve() to minimize backend buffering.
    Supports automatic reconnection with exponential backoff.
    """
    def __init__(self, source, reconnect_max_backoff=30.0):
        self.source = source
        self.reconnect_max_backoff = reconnect_max_backoff
        
        self.lock = threading.Lock()
        self._latest_frame = None
        self._latest_capture_time = 0.0
        self._latest_frame_id = 0
        
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._reader, daemon=True)
        
        # Telemetry
        self.frames_received = 0
        self.frames_decoded = 0
        self.frames_dropped_stale = 0
        self.reconnect_count = 0
        self._t_start = time.perf_counter()

    def start(self):
        self.thread.start()
        return self

    def _reader(self):
        backoff = 1.0
        
        while not self.stop_event.is_set():
            cap = cv2.VideoCapture(self.source)
            # Try to force smallest buffer
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if not cap.isOpened():
                print(f"LiveCapture: Connection failed. Retrying in {backoff}s...")
                time.sleep(backoff)
                backoff = min(backoff * 2, self.reconnect_max_backoff)
                self.reconnect_count += 1
                continue

            print(f"LiveCapture: Connected to {self.source}")
            backoff = 1.0  # Reset backoff on success
            
            while not self.stop_event.is_set():
                # grab() simply drains the hardware/backend buffer as fast as possible
                # without decoding the JPEG/h264 payload.
                grabbed = cap.grab()
                capture_monotonic_time = time.perf_counter()
                
                if not grabbed:
                    print("LiveCapture: Stream ended or read failed. Reconnecting...")
                    break
                
                self.frames_received += 1

                # Decode the payload into raw BGR
                retrieved, frame = cap.retrieve()
                if not retrieved:
                    print("LiveCapture: Retrieve failed. Reconnecting...")
                    break
                    
                self.frames_decoded += 1
                
                with self.lock:
                    if self._latest_frame is not None:
                        self.frames_dropped_stale += 1
                        
                    self._latest_frame = frame
                    self._latest_capture_time = capture_monotonic_time
                    self._latest_frame_id += 1

            cap.release()
            time.sleep(0.5)

    def read(self):
        """
        Returns (frame_id, frame, capture_time).
        Returns None if no fresh frame is available.
        Clears the slot so the same frame is never returned twice.
        """
        with self.lock:
            if self._latest_frame is None:
                return None
                
            frame = self._latest_frame
            capture_time = self._latest_capture_time
            frame_id = self._latest_frame_id
            
            self._latest_frame = None
            
            return frame_id, frame, capture_time

    def stop(self):
        self.stop_event.set()
        
    @property
    def capture_fps(self):
        elapsed = max(time.perf_counter() - self._t_start, 0.001)
        return self.frames_received / elapsed
