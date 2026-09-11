import json
import socket
import struct
import threading
import time
from collections import deque
import cv2

def recv_exact(sock: socket.socket, size: int) -> bytes:
    data = bytearray()
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("OCR server disconnected.")
        data.extend(chunk)
    return bytes(data)

def recv_message(sock: socket.socket) -> dict:
    header = recv_exact(sock, 4)
    size = struct.unpack("!I", header)[0]
    payload = recv_exact(sock, size)
    return json.loads(payload.decode("utf-8"))

def send_message(sock: socket.socket, message: dict) -> None:
    payload = json.dumps(message, separators=(",", ":")).encode("utf-8")
    header = struct.pack("!I", len(payload))
    sock.sendall(header + payload)

class OCRClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765, retries: int = 30, retry_delay: float = 2.0):
        self.sock = None
        for attempt in range(retries):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.settimeout(5.0)
                sock.connect((host, port))
                sock.settimeout(None)
                self.sock = sock
                print(f"OCRClient: connected to {host}:{port} on attempt {attempt + 1}", flush=True)
                break
            except (ConnectionRefusedError, TimeoutError, OSError) as e:
                if attempt < retries - 1:
                    print(f"OCRClient: waiting for OCR server ({e}) — retry {attempt+1}/{retries} in {retry_delay}s...", flush=True)
                    time.sleep(retry_delay)
                else:
                    raise RuntimeError(f"OCRClient: could not connect to {host}:{port} after {retries} attempts: {e}") from e
        self.request_counter = 0
        self.lock = threading.Lock()

    def submit(self, items: list[dict]) -> int:
        if not items:
            return -1
        self.request_counter += 1
        request_id = self.request_counter
        encoded_items = []
        for item in items:
            crop = item["crop"]
            ok, buffer = cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ok:
                continue
            encoded_items.append({
                "track_id": int(item["track_id"]),
                "frame_id": int(item["frame_id"]),
                "image_hex": buffer.tobytes().hex(),
            })
        if not encoded_items:
            return -1
        message = {"request_id": request_id, "items": encoded_items}
        with self.lock:
            send_message(self.sock, message)
        return request_id

    def receive(self, timeout: float | None = None) -> dict:
        previous_timeout = self.sock.gettimeout()
        self.sock.settimeout(timeout)
        try:
            return recv_message(self.sock)
        finally:
            self.sock.settimeout(previous_timeout)

    def close(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            self.sock.close()
        except OSError:
            pass

class OCRWorker:
    def __init__(self, client: OCRClient, max_queue: int = 8):
        self.client = client
        self.queue = deque(maxlen=max_queue)
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.result_queue = deque()
        self.result_lock = threading.Lock()
        
        self.jobs_submitted = 0
        self.jobs_dequeued = 0
        self.jobs_sent = 0
        self.jobs_received = 0
        self.jobs_completed = 0
        self.jobs_dropped = 0
        self.ocr_round_trip_ms = 0.0
        
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()
        return self

    def submit(self, items: list[dict]):
        if not items:
            return
        with self.lock:
            for item in items:
                if len(self.queue) >= self.queue.maxlen:
                    self.queue.popleft()
                    self.jobs_dropped += 1
                self.queue.append(item)
                self.jobs_submitted += 1

    def pop_results(self) -> list[dict]:
        with self.result_lock:
            results = list(self.result_queue)
            self.result_queue.clear()
        return results

    def _run(self):
        last_submit_time = time.perf_counter()
        while not self.stop_event.is_set():
            batch = []
            with self.lock:
                now = time.perf_counter()
                time_since_last = now - last_submit_time
                # If we have 8 items, OR we have items and 10ms has passed (was 50ms — lower latency)
                if len(self.queue) >= 8 or (self.queue and time_since_last > 0.010):
                    while self.queue and len(batch) < 8:
                        batch.append(self.queue.popleft())
                    self.jobs_dequeued += len(batch)
            
            if not batch:
                time.sleep(0.002)
                continue
            
            try:
                t0 = time.perf_counter()
                request_id = self.client.submit(batch)
                if request_id < 0:
                    continue
                self.jobs_sent += len(batch)
                last_submit_time = time.perf_counter()
                
                response = self.client.receive(timeout=None)
                t1 = time.perf_counter()
                
                self.jobs_received += 1
                self.ocr_round_trip_ms = (t1 - t0) * 1000.0
                results = response.get("results", [])
                
                with self.result_lock:
                    self.result_queue.extend(results)
                    self.jobs_completed += len(results)
            except Exception as exc:
                print(f"[OCR WORKER] {exc}", flush=True)

    def stop(self):
        self.stop_event.set()
