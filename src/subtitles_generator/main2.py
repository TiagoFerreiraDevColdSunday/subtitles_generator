import asyncio
import json
import os
import argparse
import signal
import sys
import time
import subprocess
from contextlib import suppress
from threading import Thread

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
        self.lang=None
        self.translate = (task == "translate")
        self.use_vad = False
        self.task = task
        self.multilingual=True
    
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
            if segs:
                print(segs, flush=True)

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

            # START MIC
            with sd.InputStream(
                samplerate=self.samplerate,
                channels=1,
                dtype="int16",
                blocksize=self.blocksize,
                callback=self._callback
            ):
                print("\n[INFO] Steaming...")
                await wait

            print("[INFO] Stopped")

def parse_args():
    p = argparse.ArgumentParser(
        description="Real-time mic → WhisperLive → transcript (no GUI)."
    )
    p.add_argument("--host", default="localhost", help="Server host if not launching local")
    p.add_argument("--port", type=int, default=9090, help="Server port")
    return p.parse_args()

def main():
    args = parse_args()


    ws_url = f"ws://localhost:{args.port}"

    asyncio.run(wait_for_ws(ws_url, timeout=30.0))

    mic = MicStreamer(ws_url)

    asyncio.run(mic.run())
    

if __name__ == "__main__":
    main()