"""Minimal Kokoro-82M (ONNX) speech synthesis from hand-written phonemes.

No espeak here, so input is misaki-style IPA (A=eɪ, I=aɪ, O=oʊ, W=aʊ, Y=ɔɪ, ʤ, ʧ, ʦ).
Usage: python3 tts.py <voice> <speed> "<phonemes>" <out.wav>
"""
import json, sys, wave
import numpy as np
import onnxruntime as ort

MODEL = "/home/claude/assets/tts/kokoro-v1.0.onnx"
VOICES = "/home/claude/assets/tts/voices-v1.0.bin"
VOCAB = json.load(open("/home/claude/vendor/kokoro-onnx/src/kokoro_onnx/config.json"))["vocab"]
SR = 24000


def synth(phonemes, voice="af_heart", speed=1.0):
    missing = sorted({c for c in phonemes if c not in VOCAB})
    if missing:
        raise ValueError(f"not in vocab: {missing}")
    tokens = [VOCAB[c] for c in phonemes]
    sess = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
    names = {i.name: i for i in sess.get_inputs()}
    tok_name = "input_ids" if "input_ids" in names else "tokens"
    style = np.load(VOICES)[voice][min(len(tokens), 510) - 1]
    out = sess.run(None, {
        tok_name: np.array([[0, *tokens, 0]], dtype=np.int64),
        "style": np.asarray(style, dtype=np.float32),
        "speed": np.array([speed], dtype=np.float32),
    })
    return np.asarray(out[0]).ravel()


def write_wav(path, audio, sr=SR):
    a = np.clip(audio / max(1e-6, np.abs(audio).max()) * 0.95, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    voice, speed, ph, out = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
    a = synth(ph, voice, speed)
    write_wav(out, a)
    print(f"{out}: {len(a) / SR:.2f}s")
