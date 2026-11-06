import sounddevice as sd
import argparse
import sys

SAMPLE_RATE = 48000
CHANNELS = 2
BLOCK_SIZE = 256
DTYPE = "float32"

statuses= []

def device_arg(value):
    if value is None:                 # the option wasn't given at all
        return None                   # None tells sounddevice: use the default device
    return int(value) if value.isdigit() else value

def audio_callback(indata, outdata, frames, time_info, status):
    if status:
        statuses.append(status)

    # Future Ripple DSP goes here.
    # Pass microphone audio directly to the headphones.
    outdata[:] = indata

def main(in_device_id, out_device_id):
    try:
        sd.check_input_settings(
            device = in_device_id,
            channels = CHANNELS,
            dtype = DTYPE, 
            samplerate = SAMPLE_RATE
        )
    except Exception as e:
        print(f"\nAudio error: {e}")
    
    try:
        sd.check_output_settings(
            device = out_device_id,
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
            while True:
                sd.sleep(1000)

    except KeyboardInterrupt:
        print("\nStopped.")
        print("\nAccumulated Audio Statuses")
        for status in statuses:
            print(f"Audio Status: {status}")

    except Exception as e:
        print(f"\nAudio error: {e}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--list", action="store_true", help="list audio devices and exit")
    p.add_argument("--in-device-id", help="input device number or ID")
    p.add_argument("--out-device-id", help="output device number or ID")
    args = p.parse_args()
    # print(args)
    # sys.exit()
 
    if args.list:
        print(sd.query_devices())
        sys.exit()

    main(device_arg(args.in_device_id), device_arg(args.out_device_id))
