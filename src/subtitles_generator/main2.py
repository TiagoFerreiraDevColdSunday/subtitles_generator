import asyncio
import json
import os
import time

import numpy as np
import sounddevice as sd
import websockets
import uuid

# POC NOTES:
# Mono: what you hear in one hear = the other
# Stereo: you hear a different sound per ear.
#
#
#
#

DEFAULT_WS = "ws://localhost:9090"

def _find_input_device_index(name_hint: str | None) -> int | None:
    """Return input device index that matches name_hint (substring), or None.

    If name_hint is None, try to auto-pick BlackHole; otherwise return None.
    """
    try:
        devices = sd.query_devices()
    except Exception:
        return None

    target = (name_hint or "BlackHole").lower() if name_hint is None or name_hint.strip() == "" else name_hint.lower()

    match_idx = None
    for idx, dev in enumerate(devices):
        name = str(dev.get("name", "")).lower()
        max_in = int(dev.get("max_input_channels", 0) or 0)
        if max_in > 0 and target in name:
            match_idx = idx
            break

    return match_idx

def _print_input_devices():
    try:
        devices = sd.query_devices()
    except Exception as e:
        print(f"[WARN] Unable to query audio devices: {e}")
        return

    print("\n[INFO] Available input devices:")
    for idx, dev in enumerate(devices):
        if int(dev.get("max_input_channels", 0) or 0) > 0:
            sr = dev.get("default_samplerate", "?")
            print(f"  [{idx}] {dev.get('name')} — channels: {dev.get('max_input_channels')} sr: {sr}")

async def wait_for_ws(host: str, timeout: float = 30.0):

    start = time.time()

    while time.time() - start <= timeout:

        try:
            async with websockets.connect(host):
                return True
        except Exception:
            await asyncio.sleep(0.5)

    print(f"{host} was not able to connect.")

class MicStreamer:

    def __init__(self, server_ws: str, samplerate=16000, block_ms=50, device=None, model="small", task="transcribe"):
        self.server_ws = server_ws
        self.samplerate = samplerate # 16 0000 Hz , audio samples per second
        self.blocksize = int(samplerate * block_ms / 1000) # How many samples to send to the server.
        self.device = device
        self.loop = None
        self.ws = None
        self.uid = str(uuid.uuid4())
        self.ready = asyncio.Event()

        self.model = model
        self.lang="ja"
        self.translate = False
        self.use_vad = True
        self.task = task
        self.multilingual=True
        self.channels = 1
        self._last_meter_ts = 0.0
        self._printed_segments = set()
    
    # For instance:
    # n_samples = 800
    # audio_samples_array <- actually contains the sample value
    def _callback(self, audio_samples_array, n_samples, t, status):

        if status:
            print(f"Current audio status: {status}", flush=True)
        
        try:
            # Retrieve mono samples:
            payload = (audio_samples_array[:, 0].astype(np.float32) / 32768.0).tobytes()

            # Send to the wb server
            asyncio.run_coroutine_threadsafe(self.ws.send(payload), self.loop)

        except Exception:
            pass

    async def _recv_loop(self):
        async for msg in self.ws:
            try:
                data = json.loads(msg)
            except Exception:
                print(msg, flush=True)

            if data.get("message") == "SERVER_READY":
                self.ready.set()
                print("[INFO] SERVER READY", flush=True)
                continue

            segs = data.get("segments") or []
            for seg in segs:
                if not seg.get("completed"):      # only print completed segments
                    continue
                key = (seg.get("start"), seg.get("end"), seg.get("text"))
                if key in self._printed_segments: # already printed this exact segment
                    continue
                print(f"Subtitles: {seg['text']}", flush=True)
                self._printed_segments.add(key)

    async def run(self):
        self.loop = asyncio.get_running_loop()

        async with websockets.connect(self.server_ws, max_size=8_388_608) as ws:
            self.ws = ws

            print(f"[INFO] Server Connect {self.server_ws}", flush=True)

            # Setup handshake

            hs = {
                "uid": self.uid,
                "language": self.lang,
                "task": self.task,
                "translate": self.translate,
                "model": self.model,    
                "use_vad": self.use_vad,
            }

            await self.ws.send(json.dumps(hs))

            print("Handshake sent", flush=True)

            wait = asyncio.create_task(self._recv_loop())

            try:
                await asyncio.wait_for(self.ready.wait(), timeout=120)
            except asyncio.TimeoutError:
                raise RuntimeError("Failed to receive signal from Server")

            # Determine channel count for selected device (prefer 2 if available)
            try:
                if self.device is not None:
                    dev_info = sd.query_devices(self.device)
                else:
                    dev_info = sd.query_devices(None, kind='input')
                max_in = int(dev_info.get("max_input_channels", 1) or 1)
                self.channels = 2 if max_in >= 2 else 1
            except Exception:
                self.channels = 1

            # START MIC
            with sd.InputStream(
                samplerate=self.samplerate,
                channels=self.channels,
                dtype="int16",
                blocksize=self.blocksize,
                device=self.device,
                callback=self._callback
            ):
                print("\n[INFO] Streaming...")
                await wait

            print("[INFO] Stopped")

def main():
    ws_url = os.environ.get("WS_URL", DEFAULT_WS)

    # Optional: pick input device. Priority: CLI/env > auto BlackHole > default
    # - Set INPUT_DEVICE_NAME to a substring like "BlackHole" or exact device name
    # - Or set INPUT_DEVICE_INDEX to a numeric index
    device_index = None
    idx_env = os.environ.get("INPUT_DEVICE_INDEX")
    name_env = os.environ.get("INPUT_DEVICE_NAME")
    if idx_env:
        try:
            device_index = int(idx_env)
        except ValueError:
            print(f"[WARN] Invalid INPUT_DEVICE_INDEX: {idx_env}")
    else:
        device_index = _find_input_device_index(name_env)

    if device_index is None:
        print("[WARN] No specific input device selected. Using system default.")
        _print_input_devices()
    else:
        try:
            dev_info = sd.query_devices(device_index)
            print(f"[INFO] Using input device [{device_index}]: {dev_info['name']}")
        except Exception:
            print(f"[WARN] Could not query device {device_index}. Proceeding anyway.")

    asyncio.run(wait_for_ws(ws_url, timeout=30.0))

    mic = MicStreamer(ws_url, device=device_index)

    asyncio.run(mic.run())
    

if __name__ == "__main__":
    main()
