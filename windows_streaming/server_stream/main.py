# Socket connection
import asyncio
import websockets
import argparse
import sys
import sounddevice as sd

URL = "wss://summit-innovative.duckdns.org/dev/stream/"
API_KEY = "c18ec4ba23d30007f7b6a304d79762db3f6f69eecc7fbded89949a6c3ac5f24c"
SEND_MES = "Is this the ripple server"
ECHO = "echo"
PROCESS = "process"
FRAMES = 256
CHANNELS = 2
DTYPE = "int16"
SAMPLE_RATE = 48000

# Loop 1 - runs forever:
#   Capture audio (256 samples)
#   Send audio
#   (don't wait for the reply)
async def sender(ws, input_stream):
    while True:
        # How do I use await?
        input_sample, status = await asyncio.to_thread(input_stream.read, FRAMES)
        # How do I send this correctly?
        await ws.send(input_sample.encode())

# Loop 2 - runs forever, at the same time as loop 1:
#   Receive audio (whenever it arrives)
#   Put it in a small playback buffer
async def receiver(ws, output_stream):
    while True:
        # How do I correctly receive this
        msg = await ws.recv()         # pauses only the receiver, not the sender
        output_stream.write(msg)


async def main(in_device_id, out_device_id):
    # Verify that devices can be used properly
    try:
        sd.check_input_settings(
            device = in_device_id,
            channels = CHANNELS,
            dtype = DTYPE, 
            samplerate = SAMPLE_RATE
        )
        sd.check_output_settings(
            device = out_device_id,
            channels = CHANNELS,
            dtype = DTYPE,
            samplerate = SAMPLE_RATE
        )
    except Exception as e:
        print(f"\nAudio Device error: {e}")

    # Set up the streams
    input_stream = sd.InputStream(
        samplerate = SAMPLE_RATE, 
        blocksize = FRAMES,
        device = in_device_id,
        channels = CHANNELS,
        dtype = DTYPE
    )

    output_stream = sd.OutputStream(
        samplerate = SAMPLE_RATE, 
        blocksize = FRAMES,
        device = out_device_id,
        channels = CHANNELS,
        dtype = DTYPE
    )
    
    # Open a socket (once)
    async with  websockets.connect(URL+PROCESS, additional_headers={"x-api-key": API_KEY}) as ws:
        await asyncio.gather(sender(ws, input_stream), receiver(ws, output_stream))   # run both at the same time
    

    

    

    # On exit: stop the audio streams, close the socket

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
 
    try:
        asyncio.run(main(args.in_device_id, args.out_device_id))
    except KeyboardInterrupt:
        print("\nAudio streaming has stopped")
        # Print status messages here