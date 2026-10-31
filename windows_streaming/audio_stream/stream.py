
import sounddevice as sd

SAMPLE_RATE = 48000
CHANNELS = 1
BLOCK_SIZE = 256


def audio_callback(indata, outdata, frames, time_info, status):
    if status:
        print(f"Audio status: {status}")

    # Future Ripple DSP goes here.
    # Pass microphone audio directly to the headphones.
    outdata[:] = indata


def main():
    print("Available audio devices:")
    print(sd.query_devices())

    print("\nDefault audio devices:")
    print(sd.query_devices(kind="input"))
    print(sd.query_devices(kind="output"))

    print("\nStarting microphone pass-through.")
    print("Press Ctrl+C to stop.")

    try:
        with sd.Stream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=CHANNELS,
            dtype="float32",
            latency="low",
            callback=audio_callback,
        ):
            while True:
                sd.sleep(1000)

    except KeyboardInterrupt:
        print("\nStopped.")

    except Exception as e:
        print(f"\nAudio error: {e}")


if __name__ == "__main__":
    main()
