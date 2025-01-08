import os
import re
from pydub import AudioSegment
# from pydub.effects import crossfade
from edge_tts import Communicate
import asyncio

# Function to parse the text file with timestamps
def parse_transcription_file(file_path):
    transcription = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match(r'\[(\d+\.\d+)\] (.+)', line.strip())
            if match:
                start_time = float(match.group(1))
                text = match.group(2)
                transcription.append((start_time, text))
    return transcription

# Function to generate speech for a text segment asynchronously
async def generate_speech(text, output_path, voice="es-ES-AlvaroNeural"):
    communicate = Communicate(text, voice)
    with open(output_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])

# Function to synthesize audio with timing
def synthesize_audio_with_timing(transcription, output_file, fade_duration=200):
    combined_audio = AudioSegment.silent(duration=0)  # Start with silence
    temp_files = []

    for i, (start_time, text) in enumerate(transcription):
        segment_start = start_time * 1000  # Convert to milliseconds

        # Generate audio for the current segment
        temp_audio_file = f"temp_segment_{i}.mp3"
        temp_files.append(temp_audio_file)
        asyncio.run(generate_speech(text, temp_audio_file))

        # Load the generated audio
        audio_segment = AudioSegment.from_file(temp_audio_file)

        # Calculate the silence duration needed before this segment
        if len(combined_audio) < segment_start:
            silence_duration = segment_start - len(combined_audio)
            combined_audio += AudioSegment.silent(duration=silence_duration)

        # Add the audio segment with a fade-in effect
        combined_audio = combined_audio.append(audio_segment, crossfade=fade_duration)

    # Export the final audio to an MP3 file
    combined_audio.export(output_file, format="mp3")

    # Remove temporary files
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)

# Main function
if __name__ == "__main__":
    transcription_file = "2025-01-07_17-48-49 output_audio_with_timestamps.txt"  # Input file path
    output_mp3_file = "output_audio.mp3"  # Output MP3 file path

    # Parse the transcription file
    transcription_data = parse_transcription_file(transcription_file)

    # Synthesize audio with timing
    synthesize_audio_with_timing(transcription_data, output_mp3_file)

    print(f"Audio file saved as {output_mp3_file}")
