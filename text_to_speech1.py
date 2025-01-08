import re
from pydub import AudioSegment
from edge_tts import Communicate
import asyncio

# Function to parse the text file with timestamps
def parse_transcription_file(file_path):
    transcription = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match(r'\[(\d+\.\d+) - (\d+\.\d+)\] (.+)', line.strip())
            if match:
                start_time = float(match.group(1))
                end_time = float(match.group(2))
                text = match.group(3)
                transcription.append((start_time, end_time, text))
    return transcription

# Function to generate speech for a text segment asynchronously
async def generate_speech(text, output_path, voice="es-ES-AlvaroNeural"):
    communicate = Communicate(text, voice)
    with open(output_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])

# Function to synthesize audio and arrange it with timing
def synthesize_audio_with_timing(transcription, output_file):
    start_silence = transcription[0][0]
    # print(start_silence)
    # combined_audio = AudioSegment.silent(duration=0)  # Start with silence
    combined_audio = AudioSegment.silent(duration=start_silence * 1000)  # Start with initial pause

    for start_time, end_time, text in transcription:
        segment_duration = (end_time - start_time) * 1000  # Convert to milliseconds

        # Generate audio for the current segment
        temp_audio_file = "temp_segment.mp3"
        asyncio.run(generate_speech(text, temp_audio_file))

        # Load the generated audio
        audio_segment = AudioSegment.from_file(temp_audio_file)

        # Trim or pad to match the desired segment duration
        if len(audio_segment) > segment_duration:
            audio_segment = audio_segment[:segment_duration]
        else:
            silence_duration = segment_duration - len(audio_segment)
            audio_segment += AudioSegment.silent(duration=silence_duration)

        # Add the segment to the combined audio
        combined_audio += audio_segment

    # Export the final audio to an MP3 file
    combined_audio.export(output_file, format="mp3")

# Main function
if __name__ == "__main__":
    transcription_file = "transcription_with_timestamps.txt"  # Input file path
    output_mp3_file = "output_audio.mp3"  # Output MP3 file path

    # Parse the transcription file
    transcription_data = parse_transcription_file(transcription_file)

    # Synthesize audio with timing
    synthesize_audio_with_timing(transcription_data, output_mp3_file)

    print(f"Audio file saved as {output_mp3_file}")
