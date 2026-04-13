import os
import json
import subprocess
from vosk import Model, KaldiRecognizer, SetLogLevel
from dotenv import load_dotenv

load_dotenv()

SetLogLevel(-1)

MODEL_PATH = os.getenv("MODEL_PATH", "vosk-model-small-ru-0.22")

if not os.path.exists(MODEL_PATH):
    raise Exception(f"Модель Vosk не найдена: {MODEL_PATH}")

model = Model(MODEL_PATH)


def transcribe_file(file_path: str):
    process = subprocess.Popen(
        [
            "ffmpeg",
            "-i", file_path,
            "-ar", "16000",
            "-ac", "1",
            "-f", "s16le",
            "-"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )

    recognizer = KaldiRecognizer(model, 16000)
    transcript = []

    while True:
        data = process.stdout.read(4000)

        if len(data) == 0:
            break

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")

            if text:
                transcript.append(text)

    final_result = json.loads(recognizer.FinalResult())

    if final_result.get("text"):
        transcript.append(final_result["text"])

    full_text = " ".join(transcript).strip()

    if not full_text:
        return "Не удалось распознать речь в файле"

    return full_text