import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer

model = Model("vosk-model-small-en-us-0.15")

# Configure recognizer
samplerate = 16000
recognizer = KaldiRecognizer(model, samplerate)

# Internal audio queue
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(f"[Mic Warning] {status}")
    q.put(bytes(indata))

def transcribe_audio():
    """Record and transcribe using Vosk with VAD (voice activity detection)"""
    print("[Mic] Listening for speech...")

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        result_text = ""
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                result_text = result.get("text", "")
                break
            # else:
            #     partial = json.loads(recognizer.PartialResult())
            #     print("...", partial.get("partial", ""))

    print(f"[STT] You said: {result_text}")
    return result_text
