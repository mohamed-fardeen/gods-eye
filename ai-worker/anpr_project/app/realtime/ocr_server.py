from __future__ import annotations

import json
import socket
import struct
import time
from pathlib import Path

import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OCR_MODEL = (
    PROJECT_ROOT
    / "models"
    / "ocr_ppocrv6_small"
    / "best_accuracy"
)

HOST = "127.0.0.1"
PORT = 8765

MAX_BATCH = 8


def recv_exact(
    sock: socket.socket,
    size: int,
) -> bytes:

    data = bytearray()

    while len(data) < size:

        chunk = sock.recv(
            size - len(data)
        )

        if not chunk:
            raise ConnectionError(
                "Socket closed."
            )

        data.extend(chunk)

    return bytes(data)


def recv_message(
    sock: socket.socket,
) -> dict:

    header = recv_exact(
        sock,
        4,
    )

    size = struct.unpack(
        "!I",
        header,
    )[0]

    payload = recv_exact(
        sock,
        size,
    )

    return json.loads(
        payload.decode("utf-8")
    )


def send_message(
    sock: socket.socket,
    message: dict,
) -> None:

    payload = json.dumps(
        message,
        separators=(",", ":"),
    ).encode("utf-8")

    header = struct.pack(
        "!I",
        len(payload),
    )

    sock.sendall(
        header + payload
    )


def clean_text(
    text: str,
) -> str:

    return "".join(
        c
        for c in str(text).upper()
        if c.isalnum()
    )



def pad_to_uniform_width(crops: list[np.ndarray]) -> list[np.ndarray]:
    if not crops: return []
    # PaddleOCR requires height=32 or 48 for most models, but uniform width is key to prevent batching crashes.
    # We find the max width, and pad the right side.
    max_w = max(crop.shape[1] for crop in crops)
    padded = []
    for crop in crops:
        h, w, c = crop.shape
        if w < max_w:
            pad = np.zeros((h, max_w - w, c), dtype=crop.dtype)
            crop = np.hstack((crop, pad))
        padded.append(crop)
    return padded

class PaddleRecognizer:

    def __init__(self):

        from paddleocr import PaddleOCR

        checkpoint = Path(
            str(OCR_MODEL) + ".pdparams"
        )

        if not checkpoint.exists():

            raise FileNotFoundError(
                f"OCR checkpoint not found:\n"
                f"{checkpoint}"
            )

        self._t_init_start = time.perf_counter()

        print("=" * 60)
        print("PERSISTENT PADDLE OCR SERVER V2")
        print("=" * 60)
        print(
            f"Checkpoint : {OCR_MODEL}"
        )

        self.ocr = PaddleOCR(
            use_angle_cls=False,
            lang="en",
            show_log=False,
            det=False,
            rec_model_dir=str(
                OCR_MODEL
            ),
            rec_batch_num=MAX_BATCH,
        )

        print(
            "PaddleOCR : READY"
        )
        print("=" * 60)

        # --------------------------------------------------------
        # EXACT PRODUCTION PATH WARMUP
        # --------------------------------------------------------
        print("Warming up OCR server...")
        _t_warmup_start = time.perf_counter()
        
        self.first_real_time = None
        
        # 1. Create a dummy image mimicking a realistic plate crop
        dummy_crop = np.zeros((48, 144, 3), dtype=np.uint8)
        # 2. Run the exact same method used in production
        # We do this twice to ensure complete CUDA stream warmup
        try:
            self.recognize_batch([dummy_crop])
            self.recognize_batch([dummy_crop, dummy_crop])
        except Exception as e:
            print(f"OCR warmup failed: {e}")
            
        _t_warmup_end = time.perf_counter()
        self.init_time = _t_warmup_start - self._t_init_start
        self.warmup_time = _t_warmup_end - _t_warmup_start
        
        print(f"OCR initialization : {self.init_time:.2f} s")
        print(f"OCR warmup         : {self.warmup_time:.2f} s")
        print("OCR Warmup complete.")
        print("=" * 60)


    def recognize_one(
        self,
        crop: np.ndarray,
    ) -> tuple[str, float]:

        if crop is None or crop.size == 0:
            return "", 0.0

        result = self.ocr.ocr(
            crop,
            det=False,
            cls=False,
        )

        if not result:
            return "", 0.0

        current = result

        while (
            isinstance(current, list)
            and len(current) == 1
            and isinstance(current[0], list)
        ):

            current = current[0]

        if isinstance(
            current,
            tuple,
        ):

            current = [
                current
            ]

        best_text = ""
        best_conf = 0.0

        for item in current:

            if not isinstance(
                item,
                (list, tuple),
            ):
                continue

            if len(item) < 2:
                continue

            text = clean_text(
                item[0]
            )

            try:

                confidence = float(
                    item[1]
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            if confidence > best_conf:

                best_text = text
                best_conf = confidence

        return (
            best_text,
            best_conf,
        )

    def recognize_batch(
        self,
        crops: list[np.ndarray],
    ) -> list[tuple[str, float]]:
        if not crops:
            return []
        try:
            _t_req_start = time.perf_counter()
            crops = pad_to_uniform_width(crops)
            results, _ = self.ocr.text_recognizer(crops)
            
            if self.first_real_time is None:
                self.first_real_time = time.perf_counter() - _t_req_start
                print(f"First real OCR : {self.first_real_time * 1000:.1f} ms")
                
            cleaned_results = []
            for item in results:
                if not item or len(item) < 2:
                    cleaned_results.append(("", 0.0))
                    continue
                text, conf = item
                cleaned_text = clean_text(text)
                try:
                    confidence = float(conf)
                except (TypeError, ValueError):
                    confidence = 0.0
                cleaned_results.append((cleaned_text, confidence))
            return cleaned_results
        except Exception as exc:
            print(f"[WARN] Batched OCR failed: {exc}")
            return [("", 0.0) for _ in crops]


def decode_crop(
    encoded: str,
) -> np.ndarray:

    raw = np.frombuffer(
        bytes.fromhex(encoded),
        dtype=np.uint8,
    )

    return cv2.imdecode(
        raw,
        cv2.IMREAD_COLOR,
    )


ocr_server_received = 0
ocr_decode_completed = 0
ocr_recognizer_started = 0
ocr_recognizer_completed = 0
ocr_response_sent = 0
ocr_server_errors = 0

def run_server():

    recognizer = (
        PaddleRecognizer()
    )

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1,
    )

    server.setsockopt(
        socket.IPPROTO_TCP,
        socket.TCP_NODELAY,
        1,
    )

    server.bind(
        (
            HOST,
            PORT,
        )
    )

    server.listen(1)

    print(
        f"OCR server listening on "
        f"{HOST}:{PORT}",
        flush=True,
    )

    while True:

        client, address = (
            server.accept()
        )

        print(
            f"OCR client connected: "
            f"{address}",
            flush=True,
        )

        try:

            while True:

                request = recv_message(
                    client
                )
                
                global ocr_server_received, ocr_decode_completed, ocr_recognizer_started, ocr_recognizer_completed, ocr_response_sent, ocr_server_errors
                ocr_server_received += 1

                request_id = int(
                    request[
                        "request_id"
                    ]
                )

                items = request.get(
                    "items",
                    [],
                )

                # Enforce bounded server batch.
                items = items[
                    :MAX_BATCH
                ]

                crops = []

                valid_items = []

                for item in items:

                    crop = decode_crop(
                        item[
                            "image_hex"
                        ]
                    )

                    if (
                        crop is None
                        or crop.size == 0
                    ):
                        continue

                    crops.append(
                        crop
                    )

                    valid_items.append(
                        item
                    )
                
                ocr_decode_completed += 1

                started = (
                    time.perf_counter()
                )
                
                ocr_recognizer_started += 1

                batch_results = (
                    recognizer.recognize_batch(
                        crops
                    )
                )
                
                ocr_recognizer_completed += 1

                elapsed_ms = (
                    time.perf_counter()
                    - started
                ) * 1000.0

                results = []

                for item, pair in zip(
                    valid_items,
                    batch_results,
                ):

                    text, confidence = pair

                    results.append(
                        {
                            "track_id": int(
                                item[
                                    "track_id"
                                ]
                            ),
                            "frame_id": int(
                                item[
                                    "frame_id"
                                ]
                            ),
                            "text": text,
                            "confidence": confidence,
                        }
                    )

                send_message(
                    client,
                    {
                        "request_id": request_id,
                        "results": results,
                        "latency_ms": elapsed_ms,
                    },
                )
                ocr_response_sent += 1

        except (
            ConnectionError,
            BrokenPipeError,
            ConnectionResetError,
            OSError,
        ) as exc:
            ocr_server_errors += 1
            print(
                f"OCR client disconnected: "
                f"{exc}",
                flush=True,
            )
            print(f"Server Stats: Rx {ocr_server_received} | Dec {ocr_decode_completed} | RecStart {ocr_recognizer_started} | RecEnd {ocr_recognizer_completed} | Tx {ocr_response_sent} | Err {ocr_server_errors}", flush=True)

        finally:

            try:
                client.close()
            except OSError:
                pass


if __name__ == "__main__":
    run_server()