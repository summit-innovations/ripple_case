import sounddevice as sd
import time

SAMPLE_RATE = 48000
BLOCK_SIZE = 256
CHANNELS = 2

underflows = 0

def callback(outdata, frames, time_info, status):
    global underflows

    if status.output_underflow:
        underflows += 1

    outdata.fill(0)

with sd.OutputStream(
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="float32",
    blocksize=BLOCK_SIZE,
    latency="low",
    callback=callback,
):
    for second in range(20):
        time.sleep(1)
        print(f"Second {second + 1}: {underflows} total underflows")