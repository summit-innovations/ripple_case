# Socket connection
import asyncio
import websockets

URL = "wss://summit-innovative.duckdns.org/stream/"
API_KEY = "c18ec4ba23d30007f7b6a304d79762db3f6f69eecc7fbded89949a6c3ac5f24c"
SEND_MES = "Is this the ripple server"

# Loop 1 - runs forever:
#   Capture audio (256 samples)
#   Send audio
#   (don't wait for the reply)
async def sender(ws):
    while True:
        await ws.send(SEND_MES.encode())
        print(f"Sent: {SEND_MES}")
        await asyncio.sleep(0.016)    # stand-in for "wait for the next 256 samples"

# Loop 2 - runs forever, at the same time as loop 1:
#   Receive audio (whenever it arrives)
#   Put it in a small playback buffer
async def receiver(ws):
    while True:
        msg = await ws.recv()         # pauses only the receiver, not the sender
        print(f"Received: {msg}")

# Playback - runs on its own, every 256 samples:
#   Take the next block from the playback buffer and play it
#   (play silence if the buffer is empty)

async def main():
    # Open a socket (once)
    async with  websockets.connect(URL, additional_headers={"x-api-key": API_KEY}) as ws:
        await asyncio.gather(sender(ws), receiver(ws))   # run both at the same time

    

    

    

    # On exit: stop the audio streams, close the socket

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAudio streaming has stopped")
        # Print status messages here