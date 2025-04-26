from pydub import AudioSegment
import torch
from torchaudio.pipelines import WAV2VEC2_ASR_BASE_960H

# Пути к файлам
input_file = "extracted_audio.mp3"
speech_file = "speech_only.mp3"
background_file = "background_only.mp3"

# Загрузка модели Wav2Vec 2.0
pipeline = WAV2VEC2_ASR_BASE_960H
model = pipeline.get_model()
labels = pipeline.get_labels()

def is_speech(chunk, threshold=0.5):
    """
    Проверяет, содержит ли аудиосегмент речь.
    """
    # Преобразование сегмента в формат модели
    chunk = chunk.set_frame_rate(16000).set_channels(1)
    tensor = torch.tensor(chunk.get_array_of_samples(), dtype=torch.float32) / 32768.0
    tensor = tensor.unsqueeze(0)  # Добавление batch dimension

    # Прогноз модели
    with torch.no_grad():
        logits, _ = model(tensor)  # Извлекаем логиты (первая часть возвращаемого кортежа)
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        speech_prob = probabilities[:, :, labels.index('|')].mean().item()  # Вероятность паузы между словами
        return speech_prob < threshold  # Если паузы мало, значит это речь

def split_audio(input_path, speech_path, background_path):
    """
    Разделение аудио на файлы с речью и фоновыми звуками.
    """
    audio = AudioSegment.from_file(input_path)
    chunk_duration = 1000  # Длительность сегмента в мс (1 секунда)

    speech_audio = AudioSegment.empty()
    background_audio = AudioSegment.empty()

    for i in range(0, len(audio), chunk_duration):
        chunk = audio[i:i + chunk_duration]
        if is_speech(chunk):
            speech_audio += chunk
        else:
            background_audio += chunk

    # Сохранение результатов
    speech_audio.export(speech_path, format="mp3")
    background_audio.export(background_path, format="mp3")

# Выполнение
split_audio(input_file, speech_file, background_file)
print(f"Файлы созданы:\nРечь: {speech_file}\nФоновые звуки: {background_file}")
