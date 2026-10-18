"""Original royalty-free background music, synthesized from scratch (numpy).

Upbeat, light, a little Japanese flavour (pentatonic pluck melody). Every track is unique
per seed, so each video gets its own BGM and nothing is copyrighted by anyone else.

Usage: python3 music.py <seconds> <seed> <out.wav> [bpm] [key]
  key: semitone offset from C (0=C, 2=D, 5=F, 7=G, 9=A ...)
"""
import sys, wave
import numpy as np
from scipy import signal

SR = 44100


def env(n, a=0.005, d=0.3, curve=6.0):
    t = np.arange(n) / SR
    e = np.exp(-curve * t / max(d, 1e-3))
    na = max(1, int(a * SR))
    e[:na] *= np.linspace(0, 1, na)
    return e


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), "low")
    return signal.lfilter(b, a, x)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def bp(x, f1, f2):
    b, a = signal.butter(2, [f1 / (SR / 2), f2 / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


# ---- instruments -------------------------------------------------------------
def kick(rng):
    n = int(0.4 * SR); t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * env(n, 0.001, 0.32, 5)
    click = hp(rng.standard_normal(n), 2000) * env(n, 0.0005, 0.01, 6) * 0.25
    return np.tanh(1.6 * (x + click))


def clap(rng):
    n = int(0.3 * SR)
    noise = bp(rng.standard_normal(n), 900, 5000)
    e = np.zeros(n)
    for off in (0, 0.011, 0.022):
        i = int(off * SR); e[i:] += env(n - i, 0.0005, 0.02 if off < 0.02 else 0.16, 5)
    tone = np.sin(2 * np.pi * 190 * np.arange(n) / SR) * env(n, 0.001, 0.06, 6) * 0.3
    return 0.55 * noise * e / 1.5 + tone


def hat(rng, open_=False):
    n = int((0.25 if open_ else 0.06) * SR)
    x = hp(rng.standard_normal(n), 7000, 4)
    return x * env(n, 0.0005, 0.18 if open_ else 0.035, 5) * 0.5


def shaker(rng):
    n = int(0.09 * SR)
    x = bp(rng.standard_normal(n), 5000, 11000)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return x * e * 0.22


def pluck(freq, dur, rng, bright=0.5):
    """Karplus-Strong string — koto/harp-like."""
    n = int(dur * SR); p = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, p) * 0.9
    buf = lp(buf, 2000 + 6000 * bright, 1)
    out = np.zeros(n); decay = 0.996
    idx = 0
    for i in range(n):
        v = buf[idx]
        nxt = buf[(idx + 1) % p]
        buf[idx] = decay * 0.5 * (v + nxt)
        out[i] = v
        idx = (idx + 1) % p
    return out * env(n, 0.001, dur, 2.5)


def epiano(freqs, dur):
    """Soft electric-piano chord: FM-ish sines with tremolo."""
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        mod = np.sin(2 * np.pi * f * 2 * t) * 1.2 * np.exp(-t * 6)
        x += np.sin(2 * np.pi * f * t + mod) * (0.9 + 0.1 * np.sin(2 * np.pi * 4.5 * t))
    return x / len(freqs) * env(n, 0.01, dur * 1.3, 2.2)


def bass(freq, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t)
    e = np.minimum(1, t / 0.006) * np.exp(-t * 2.2)
    e[-int(0.015 * SR):] *= np.linspace(1, 0, int(0.015 * SR))
    return np.tanh(1.4 * x * e) * 0.8


def reverb(x, rng, secs=1.6, wet=0.22):
    n = int(secs * SR); t = np.arange(n) / SR
    out = []
    for ch in range(2):
        ir = rng.standard_normal(n) * np.exp(-t * 4.2)
        ir = lp(ir, 6000); ir[: int(0.012 * SR)] = 0
        ir /= np.sqrt((ir ** 2).sum())
        out.append(signal.fftconvolve(x, ir)[: len(x)])
    return np.stack(out) * wet


# ---- arrangement -------------------------------------------------------------
PROGRESSIONS = [
    [0, 7, 9, 5],     # I  V  vi IV
    [0, 9, 5, 7],     # I  vi IV V
    [5, 7, 0, 9],     # IV V  I  vi
    [0, 5, 9, 7],     # I  IV vi V
]
PENTA = [0, 2, 4, 7, 9]   # major pentatonic


def chord_notes(root, base=60):
    # diatonic triad + add9 flavour built on scale degree root (semitones from tonic)
    major = {0: [0, 4, 7, 14], 5: [0, 4, 7, 14], 7: [0, 4, 7, 10], 9: [0, 3, 7, 14], 2: [0, 3, 7, 10], 4: [0, 3, 7, 10]}
    return [base + root + i for i in major.get(root, [0, 4, 7])]


def make(seconds, seed, bpm=None, key=None):
    rng = np.random.default_rng(seed)
    bpm = bpm or int(rng.choice([104, 108, 112, 116, 120]))
    key = key if key is not None else int(rng.choice([0, 2, 5, 7, 9]))
    prog = PROGRESSIONS[seed % len(PROGRESSIONS)]
    beat = 60 / bpm; bar = 4 * beat
    swing = 0.06 * beat if seed % 2 else 0.0
    nbars = int(np.ceil(seconds / bar)) + 1
    N = int((nbars * bar + 2) * SR)
    drums, music, low = np.zeros(N), np.zeros(N), np.zeros(N)

    def put(buf, x, t, g=1.0):
        i = int(t * SR); j = min(N, i + len(x))
        if i < N: buf[i:j] += g * x[: j - i]

    K, C = kick(rng), clap(rng)
    hats = [hat(rng) for _ in range(4)]; ohat = hat(rng, True)
    # 2-bar melodic motif, repeated with small variations
    motif = []
    for s in range(16):
        if rng.random() < 0.55 or s % 4 == 0:
            deg = PENTA[int(rng.integers(0, 5))] + 12 * int(rng.integers(0, 2))
            motif.append((s, deg, 0.4 + 0.6 * rng.random()))
    plucks = {}

    for b in range(nbars):
        t0 = b * bar
        root = prog[b % 4]
        intro = b == 0
        # chords
        put(music, epiano([midi_hz(m + key) for m in chord_notes(root, 57)], bar), t0, 0.6)
        if b % 2 == 1:
            put(music, epiano([midi_hz(m + key) for m in chord_notes(root, 57)], beat * 1.5), t0 + 2.5 * beat, 0.3)
        # bass (root, octave pops)
        if not intro:
            for i, (pos, oct_, d) in enumerate([(0, 0, 0.9), (1.5, 0, 0.4), (2, 0, 0.9), (3.5, 12, 0.3)]):
                put(low, bass(midi_hz(36 + key + root % 12 + oct_), d * beat), t0 + pos * beat, 0.38)
        # drums
        for q in range(4):
            if not intro or q == 3:
                put(drums, K, t0 + q * beat, 0.9 if not intro else 0.5)
            if q in (1, 3) and not intro:
                put(drums, C, t0 + q * beat, 0.8)
        for e in range(8):
            off = swing if e % 2 else 0
            put(drums, hats[e % 4], t0 + e * beat / 2 + off, 0.35 if e % 2 else 0.22)
            if not intro:
                put(drums, shaker(rng), t0 + e * beat / 2 + beat / 4 + off, 0.5)
        if b % 4 == 3:
            put(drums, ohat, t0 + 3.5 * beat, 0.3)
        # melody: from bar 2, motif over 2 bars
        if b >= 1:
            half = b % 2
            for s, deg, vel in motif:
                if s // 8 != half:
                    continue
                # nudge melody notes to fit the chord tone where they land
                m = 72 + key + deg
                if (deg % 12) not in [(n - 57 - root) % 12 for n in chord_notes(root, 57)] and rng.random() < 0.3:
                    m += 2 if deg % 12 in (0, 7) else -2
                if m not in plucks:
                    plucks[m] = pluck(midi_hz(m), beat * 2, np.random.default_rng(m), bright=0.85)
                put(music, plucks[m], t0 + (s % 8) * beat / 2 + (swing if s % 2 else 0), 0.55 * vel)

    # mix: sidechain-ish ducking on music/bass from kick positions
    duck = np.ones(N)
    for b in range(nbars):
        for q in range(4):
            i = int((b * bar + q * beat) * SR); n = int(0.18 * SR)
            if i + n < N and b > 0:
                duck[i:i + n] *= 1 - 0.35 * np.exp(-np.arange(n) / SR * 18)
    dry = drums + (music + low) * duck
    st = np.stack([dry, dry]) + reverb(music, rng, wet=0.35) + reverb(drums * 0.4, rng, 0.8, 0.12)
    st[0] += 0.12 * np.roll(music, int(0.011 * SR)); st[1] += 0.12 * np.roll(music, int(0.017 * SR))
    st = st + 0.9 * np.stack([hp(st[0], 2500), hp(st[1], 2500)])   # presence lift
    st = np.tanh(st * 1.1)
    L = int(seconds * SR)
    st = st[:, :L]
    fade = int(1.5 * SR)
    st[:, -fade:] *= np.linspace(1, 0, fade) ** 1.5
    st[:, : int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR))
    rms = np.sqrt((st ** 2).mean())
    st *= 10 ** (-14 / 20) / max(rms, 1e-6)    # ~ -14 dBFS RMS
    st = np.clip(st, -0.98, 0.98)
    return st, bpm, key


def write(path, st):
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st.T * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    secs, seed, out = float(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    bpm = int(sys.argv[4]) if len(sys.argv) > 4 else None
    key = int(sys.argv[5]) if len(sys.argv) > 5 else None
    st, bpm, key = make(secs, seed, bpm, key)
    write(out, st)
    print(f"{out}: {secs}s, bpm={bpm}, key={key}, seed={seed}")
