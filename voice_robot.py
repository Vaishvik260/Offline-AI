import sounddevice as sd
import queue
import vosk
import json
import os
from langchain_community.llms import Ollama

# -------------------------------
# AI Brain
llm = Ollama(model="mistral")

# macOS TTS function
def speak(text):
    os.system(f'say "{text}"')
# -------------------------------

# -------------------------------
# Vosk microphone setup
q = queue.Queue()
model = vosk.Model("vosk-model")  # make sure this folder exists
samplerate = 16000
device = None  # default microphone

def callback(indata, frames, time, status):
    q.put(bytes(indata))

# Start listening
with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device,
                       dtype='int16', channels=1, callback=callback):
    rec = vosk.KaldiRecognizer(model, samplerate)
    print("🤖 Mini Desktop Robot is online! Say 'exit' to quit.")

    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "")
            if text:
                print("\nYou:", text)

                if "exit" in text.lower():
                    print("🤖 Goodbye!")
                    break

                # Ask Ollama
                response = llm.invoke(text)

                # Handle dict/string return
                if isinstance(response, dict) and "content" in response:
                    answer = response["content"]
                else:
                    answer = str(response)

                print("Robot:", answer)
                speak(answer)

