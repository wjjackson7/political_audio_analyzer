#!/usr/bin/env python3
from enum import Enum
from typing import List
from pydantic import BaseModel
from openai import OpenAI
import whisper
import os
import sys
import time
import wave
import threading
import contextlib
from tqdm import tqdm
from pydub import AudioSegment
from pyannote.audio.pipelines.speaker_diarization import SpeakerDiarization
from pyannote.core import Segment
import warnings
import urllib3

def seconds_to_hms(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def get_audio_duration(file_path):
    with contextlib.closing(wave.open(file_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
    return duration

def splice_audio(path):
    audio = AudioSegment.from_file(path)
    five_min_audio = audio[:300000]

    output_path = "/Users/willjackson/git/inventory_app/clip.wav"
    five_min_audio.export(output_path, format="wav")

    return output_path

def convert_audio_to_wav(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="wav")

    print(f"Audio converted to WAV and saved to {output_path}")

def get_transcript(path,filename):
    audio_path = os.path.join(path, filename.replace(".m4a", ".wav"))
    print(audio_path)
    start_time = time.time()
    model = whisper.load_model("base")

    # Get audio duration
    try:
        total_duration = get_audio_duration(audio_path)
    except:
        print("Could not determine audio duration. Defaulting to estimated time.")
        total_duration = 300  # Assume 5 minutes if metadata is unavailable

    # Start Speaker Diarization with a Progress Bar
    print("Performing speaker diarization...\n")
    diarization_pipeline = SpeakerDiarization.from_pretrained(
        "pyannote/speaker-diarization", 
        use_auth_token=os.getenv("HUGGING_FACE_HUB_TOKEN")
    )

    # Create a separate thread to run diarization while showing a progress bar
    diarization_result = []

    
    def run_diarization():
        try:
            diarization_result.append(diarization_pipeline(audio_path))
        except Exception as e:
            print(f"Error during diarization: {e}")

    diarization_thread = threading.Thread(target=run_diarization)
    diarization_thread.start()
    diarization_thread.join()  # Wait for thread to finish

    # Get the result
    if diarization_result:
        diarization = diarization_result[0]

        # Extract speaker segments
        speaker_timestamps = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_timestamps.append((turn.start, turn.end, speaker))
    else:
        print("Diarization failed or returned no result.")
        speaker_timestamps = []

    print(f"Detected {len(set(speaker for _, _, speaker in speaker_timestamps))} speakers.")
    print(f"Transcribing: {audio_path}")
    
    # Run Whisper transcription and track progress by actual segments
    transcription = model.transcribe(audio_path, verbose=True)
    
    # Update progress bar based on Whisper’s transcribed segments
    progress_bar = tqdm(total=total_duration, bar_format="{l_bar}{bar} {n_fmt}/{total_fmt} sec", ncols=80)

    last_progress = 0
    for segment in transcription.get("segments", []):
        segment_progress = min(segment["end"], total_duration)  # Ensure it doesn't exceed total time
        progress_bar.update(segment_progress - last_progress)
        progress_bar.set_description(f"{seconds_to_hms(segment['end'])} -> {seconds_to_hms(total_duration)}")
        last_progress = segment_progress

    progress_bar.close()

    # Split transcript into words with timestamps
    words_with_timestamps = transcription.get("segments", [])

    # Assign speaker labels to correct text segments
    final_transcript = []
    for start, end, speaker in speaker_timestamps:
        segment_text = " ".join(
            word["text"] for word in words_with_timestamps if start <= word["start"] <= end
        )

        if segment_text.strip():
            speaker_label = f"Speaker {speaker}:"
            final_transcript.append(f"[{seconds_to_hms(start)} - {seconds_to_hms(end)}] {speaker_label} {segment_text}")

    # Save transcript to file
    output_path = os.path.join(path, filename.replace(".wav", ".txt"))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(final_transcript))

    return "\n".join(final_transcript)

def loop_through_directory(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".m4a"):
                file_path = os.path.join(dirpath, filename)
                convert_audio_to_wav(file_path,os.path.join(dirpath, filename.replace(".m4a", ".wav")))
                get_transcript(dirpath,filename.replace(".m4a", ".wav"))
                exit()