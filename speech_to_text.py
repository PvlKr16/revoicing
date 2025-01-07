import whisper
from googletrans import Translator
from time import gmtime, strftime

translator = Translator()

# Укажите путь к вашему MP3 файлу
audio_file_path = "extracted_audio.mp3"
# audio_file_path = "output_audio.mp3"


# Загружаем модель Whisper
model = whisper.load_model("base")

# Транскрибируем аудио с таймингами
result = model.transcribe(audio_file_path, word_timestamps=True)

# Выводим текст с таймингами
# for segment in result["segments"]:
#     print(f"[{segment['start']:.2f} - {segment['end']:.2f}] {segment['text']}")
cur_time = strftime("%Y-%m-%d_%H-%M-%S", gmtime())

with open(f"{cur_time} output_audio_with_timestamps.txt", "w", encoding="utf-8") as f:
    for segment in result["segments"]:
        text_to_translate = segment['text']
        translated_text = translator.translate(text_to_translate, dest="es").text
        # f.write(f"[{segment['start']:.2f} - {segment['end']:.2f}] {translated_text}\n")
        f.write(f"[{segment['start']:.2f}] {translated_text}\n")
        # f.write(f"[{segment['start']:.2f} - {segment['end']:.2f}] {segment['text']}\n")
