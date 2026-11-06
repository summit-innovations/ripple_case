import sounddevice as sd
import numpy as np
import argparse
import sys

SAMPLE_RATE = 48000
IN_CHANNELS = 8               # UMA-8 RAW mode: 7 MEMS mics + 1 spare PDM input
OUT_CHANNELS = 2              # headphones
BLOCK_SIZE = 256              # hop size; the FFT is twice this
DTYPE = "float32"

# --- UMA-8 array geometry ---------------------------------------------------
# 1 centre mic + 6 mics on a 43 mm ring (hexagon), looking down from the top.
# Front = away from the USB cable = 12 o'clock = the beam direction.
# Axes: x = front, y = left. Angles are degrees from front, positive to the left.
# Mic 1 is directly right; going clockwise in 60-degree steps gives mics 2-6,
# so the beam sits halfway between mic 5 (30 deg left) and mic 6 (30 deg right).
# Mic N is assumed to arrive on USB channel N; verify with --levels.
CENTER_CHANNEL = 0                   # mic 0, centre of the array
RING_MIC_ANGLES_DEG = {              # USB channel: angle of that mic
    1: -90.0,                        # 3 o'clock, directly right
    2: -150.0,                       # 5 o'clock, back right
    3: 150.0,                        # 7 o'clock, back left
    4: 90.0,                         # 9 o'clock, directly left
    5: 30.0,                         # 11 o'clock, front left
    6: -30.0,                        # 1 o'clock, front right
}
SPARE_CHANNEL = 7                    # spare PDM input, ignored
RING_RADIUS = 0.043                  # metres

LOOK_AZIMUTH_DEG = 0.0               # beam direction; 0 = front (+x)
SPEED_OF_SOUND = 343.0               # m/s
DIAGONAL_LOADING = 0.05              # higher = less hiss, wider beam
OUTPUT_GAIN = 8.0                    # RAW mode has no digital gain, so boost here

statuses = []
beamformer = None


def device_arg(value):
    if value is None:                 # the option wasn't given at all
        return None                   # None tells sounddevice: use the default device
    return int(value) if value.isdigit() else value


# --- Beamformer ----------------------------------------------------------------
def mic_layout():
    """Return (channel indices, mic xy positions in metres) for the 7 mics."""
    ring_channels = list(RING_MIC_ANGLES_DEG)
    angles = np.radians(list(RING_MIC_ANGLES_DEG.values()))
    ring = RING_RADIUS * np.stack([np.cos(angles), np.sin(angles)], axis=1)
    positions = np.vstack([[0.0, 0.0], ring])
    channels = [CENTER_CHANNEL] + ring_channels
    return channels, positions


def steering_vectors(positions, azimuth_deg, freqs):
    """Phase of a plane wave from azimuth_deg at each mic, shape (F, M)."""
    az = np.radians(azimuth_deg)
    direction = np.array([np.cos(az), np.sin(az)])
    advance = positions @ direction / SPEED_OF_SOUND
    return np.exp(2j * np.pi * freqs[:, None] * advance[None, :])


def design_weights(positions, azimuth_deg, method, n_fft):
    """Per-frequency weights w, shape (F, M). Beam output is Y = w^H X."""
    freqs = np.fft.rfftfreq(n_fft, 1 / SAMPLE_RATE)
    d = steering_vectors(positions, azimuth_deg, freqs)
    m = len(positions)

    if method == "das":                       # delay-and-sum
        return d / m

    # Superdirective (MVDR against diffuse noise): narrower beam at low frequencies
    dist = np.linalg.norm(positions[:, None] - positions[None, :], axis=-1)
    w = np.empty_like(d)
    for k, f in enumerate(freqs):
        gamma = np.sinc(2 * f * dist / SPEED_OF_SOUND) + DIAGONAL_LOADING * np.eye(m)
        g_inv_d = np.linalg.solve(gamma, d[k])
        w[k] = g_inv_d / (d[k].conj() @ g_inv_d)
    return w


class StreamingBeamformer:
    """Overlap-add STFT beamformer: 7 mic channels in, 1 beam out."""

    def __init__(self, weights, hop):
        self.hop = hop
        self.n_fft = 2 * hop
        self.window = np.sqrt(np.hanning(self.n_fft + 1)[:-1]).astype(np.float32)
        self.w_h = weights.conj().astype(np.complex64)
        self.in_buf = np.zeros((self.n_fft, weights.shape[1]), np.float32)
        self.out_buf = np.zeros(self.n_fft, np.float32)

    def process(self, block):
        h = self.hop
        self.in_buf[:-h] = self.in_buf[h:]
        self.in_buf[-h:] = block

        spec = np.fft.rfft(self.in_buf * self.window[:, None], axis=0)
        beam = np.einsum("fm,fm->f", self.w_h, spec)
        frame = np.fft.irfft(beam, n=self.n_fft).astype(np.float32) * self.window

        self.out_buf += frame
        out = self.out_buf[:h].copy()
        self.out_buf[:-h] = self.out_buf[h:]
        self.out_buf[-h:] = 0.0
        return out


def print_beampattern(method):
    """Print the beam's response (dB) vs azimuth so you can see the cone width."""
    _, positions = mic_layout()
    n_fft = 2 * BLOCK_SIZE
    w = design_weights(positions, LOOK_AZIMUTH_DEG, method, n_fft)
    freqs = np.fft.rfftfreq(n_fft, 1 / SAMPLE_RATE)
    azimuths = np.arange(0, 181, 15)

    print(f"{method}: response in dB vs azimuth (degrees from front)\n")
    print("  freq  " + "".join(f"{a:>6}" for a in azimuths) + "   white-noise gain")
    for f in (250, 500, 1000, 2000, 4000, 8000):
        k = int(np.argmin(np.abs(freqs - f)))
        row = []
        for az in azimuths:
            d = steering_vectors(positions, LOOK_AZIMUTH_DEG + az, freqs[k:k + 1])[0]
            row.append(20 * np.log10(abs(w[k].conj() @ d) + 1e-12))
        wng = 10 * np.log10(1 / np.sum(abs(w[k]) ** 2))
        print(f"{freqs[k]:6.0f}  " + "".join(f"{r:6.1f}" for r in row) + f"   {wng:6.1f} dB")
    print("\nWhite-noise gain below 0 dB means mic self-noise is boosted;"
          "\nraise DIAGONAL_LOADING if the output hisses.")


# --- Audio -------------------------------------------------------------------------
def audio_callback(indata, outdata, frames, time_info, status):
    if status:
        statuses.append(status)

    if frames != BLOCK_SIZE:
        outdata.fill(0)
        return

    # Ripple DSP: beamform the 7 mic channels (spare channel dropped).
    mics = indata[:, beamformer.channels]
    beam = beamformer.process(mics) * OUTPUT_GAIN
    np.clip(beam, -1.0, 1.0, out=beam)
    outdata[:] = beam[:, None]        # same mono beam to both headphone channels


def show_levels(in_device_id):
    """Print live per-channel levels, to find the spare channel and map the mics."""
    print("\nPer-channel level in dBFS. Tap each mic to see which channel it is.")
    print("The spare channel stays silent. Press Ctrl+C to stop.\n")
    print("  ".join(f"ch{c:<5}" for c in range(IN_CHANNELS)))

    def callback(indata, frames, time_info, status):
        rms = np.sqrt(np.mean(indata ** 2, axis=0)) + 1e-12
        print("  ".join(f"{20 * np.log10(r):6.1f} " for r in rms), end="\r", flush=True)

    try:
        with sd.InputStream(device=in_device_id, samplerate=SAMPLE_RATE,
                            channels=IN_CHANNELS, dtype=DTYPE,
                            blocksize=SAMPLE_RATE // 10, callback=callback):
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\nStopped.")


def main(in_device_id, out_device_id, method):
    global beamformer

    try:
        sd.check_input_settings(
            device = in_device_id,
            channels = IN_CHANNELS,
            dtype = DTYPE,
            samplerate = SAMPLE_RATE
        )
    except Exception as e:
        print(f"\nAudio error: {e}")
        print("Is the UMA-8 running the RAW firmware (micArray_vf_raw)?")
        return

    try:
        sd.check_output_settings(
            device = out_device_id,
            channels = OUT_CHANNELS,
            dtype = DTYPE,
            samplerate = SAMPLE_RATE
        )
    except Exception as e:
        print(f"\nAudio error: {e}")
        return

    channels, positions = mic_layout()
    weights = design_weights(positions, LOOK_AZIMUTH_DEG, method, 2 * BLOCK_SIZE)
    beamformer = StreamingBeamformer(weights, BLOCK_SIZE)
    beamformer.channels = channels

    print(f"\nStarting {method} beamformer (7 mics -> headphones).")
    print("Press Ctrl+C to stop.")

    try:
        with sd.Stream(
            device=(in_device_id, out_device_id),
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=(IN_CHANNELS, OUT_CHANNELS),
            dtype=DTYPE,
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
    p.add_argument("--method", choices=["superdirective", "das"], default="superdirective",
                   help="beamformer design (default: superdirective)")
    p.add_argument("--levels", action="store_true",
                   help="show live per-channel input levels and exit")
    p.add_argument("--pattern", action="store_true",
                   help="print the beam pattern for this array and exit")
    args = p.parse_args()

    if args.list:
        print(sd.query_devices())
        sys.exit()

    if args.pattern:
        print_beampattern(args.method)
        sys.exit()

    if args.levels:
        show_levels(device_arg(args.in_device_id))
        sys.exit()

    main(device_arg(args.in_device_id), device_arg(args.out_device_id), args.method)
    