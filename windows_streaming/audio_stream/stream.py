
import sounddevice as sd

SAMPLE_RATE = 48000
CHANNELS = 2
BLOCK_SIZE = 256
DTYPE = "float32"

statuses= []
input_statuses = []
output_statuses = []

def audio_callback(indata, outdata, frames, time_info, status):
    if status:
        statuses.append(status)

    # Future Ripple DSP goes here.
    # Pass microphone audio directly to the headphones.
    outdata[:] = indata

def input_callback(indata, frames, time_info, status):
    # Do nothing right now
    if status:
        input_statuses.append(status)

def output_callback(outdata, frames, time_info, status):
    # Do nothing right now
    if status:
        output_statuses.append(status)
    
    outdata.fill(0)

def main():
    # print("Available audio devices:")
    # print(sd.query_devices())

    print("\nDefault audio devices:")
    print(sd.query_devices(kind="input"))
    print(sd.query_devices(kind="output"))

    try:
        sd.check_input_settings(
            device = 1,
            channels = CHANNELS,
            dtype = DTYPE, 
            samplerate = SAMPLE_RATE
        )
    except Exception as e:
        print(f"\nAudio error: {e}")
    
    try:
        sd.check_output_settings(
            device = 5,
            channels = CHANNELS,
            dtype = DTYPE, 
            samplerate = SAMPLE_RATE
        )
    except Exception as e:
        print(f"\nAudio error: {e}")

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
        # with sd.RawStream(
        #     samplerate=SAMPLE_RATE,
        #     blocksize=BLOCK_SIZE,
        #     channels=CHANNELS,
        #     dtype="float32",
        #     latency="low",
        #     callback=audio_callback,
        # ):
        # with sd.InputStream(
        #     samplerate = SAMPLE_RATE,
        #     blocksize = BLOCK_SIZE,
        #     channels = CHANNELS,
        #     dtype = DTYPE,
        #     latency = "low",
        #     callback = input_callback
        # ):
        # with sd.OutputStream(
        #     samplerate = SAMPLE_RATE,
        #     blocksize = BLOCK_SIZE,
        #     channels = CHANNELS,
        #     dtype = DTYPE,
        #     latency = "low",
        #     callback = output_callback
        # ):
            while True:
                sd.sleep(1000)

    except KeyboardInterrupt:
        print("\nStopped.")
        print("\nAccumulated Audio Statuses")
        for status in statuses:
            print(f"Audio Status: {status}")
        # for status in input_statuses: 
            # print(f"Audio Status: {status}")
        # for status in output_statuses: 
        #     print(f"Audio Status: {status}")

    except Exception as e:
        print(f"\nAudio error: {e}")


if __name__ == "__main__":
    main()
