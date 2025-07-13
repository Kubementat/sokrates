# This script provides utilities for voice interaction, including
# audio recording, playback, and speech-to-text transcription using
# the Whisper model. It integrates with LLM API for voice-based chat
# and uses `pyaudio` for audio input/output.

import whisper
import pyaudio
import wave
import threading
import tempfile
import os
import time
import re
import asyncio
import logging
import sys

# debug
import traceback

from enum import Enum
from .colors import Colors # Use existing Colors from llm_tools
from .output_printer import OutputPrinter # Import OutputPrinter
from pathlib import Path

# Configure logging
logging.basicConfig(filename='llm_tools_voice.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class WhisperModel(Enum):
    """
    Enum for available Whisper models.
    """
    BASE = "base"
    TINY = "tiny"
    MEDIUM = "medium"
    LARGE = "large"

class AudioRecorder:
    """
    Handles audio recording and saving to a WAV file.
    """
    def __init__(self, model: str = WhisperModel.BASE.value):
        """
        Initializes the AudioRecorder.

        Args:
            model (str): The Whisper model to use for speech-to-text. Defaults to "base".
        """
        self.chunk = 1024
        self.sample_format = pyaudio.paInt16
        self.channels = 1
        self.fs = 44100
        self.recording = False
        self.frames = []
        self.speech_to_text_model = model
        self.acknowledge_signal_filepath = str(Path(f"{Path(__file__).parent.resolve()}/../assets/signal.wav").resolve())
        
    def record_audio(self):
        """
        Records audio from the microphone until `self.recording` is set to False.
        """
        p = pyaudio.PyAudio()
        stream = p.open(format=self.sample_format,
                       channels=self.channels,
                       rate=self.fs,
                       frames_per_buffer=self.chunk,
                       input=True)
        
        self.frames = []
        while self.recording:
            data = stream.read(self.chunk)
            self.frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
    
    def save_recording(self, filename: str):
        """
        Saves the recorded audio frames to a WAV file.

        Args:
            filename (str): The path to the output WAV file.
        """
        p = pyaudio.PyAudio()
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        p.terminate()

def play_audio_file(filename: str):
    """
    Plays an audio file.

    Args:
        filename (str): The path to the audio file to play.
    """
    chunk = 1024
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()

async def run_voice_chat(llm_api, model: str, temperature: float, max_tokens: int, conversation_history: list, log_files: list, hide_reasoning: bool, verbose: bool, refiner):
    """
    Runs a voice-based chat interaction with an LLM.

    Args:
        llm_api: An instance of LLMApi for interacting with the LLM.
        model (str): The LLM model to use for chat.
        temperature (float): The sampling temperature for LLM responses.
        max_tokens (int): The maximum number of tokens for LLM responses.
        conversation_history (list): A list of message dictionaries representing the conversation history.
        log_files (list): A list of file objects to log the conversation.
        hide_reasoning (bool): If True, hides LLM's internal reasoning (e.g., <think> tags).
        verbose (bool): If True, enables verbose output.
        refiner: An instance of PromptRefiner for cleaning LLM responses.
    """
    recorder = AudioRecorder()
    OutputPrinter.print_info("Loading Whisper model...", "")
    try:
        whisper_model = whisper.load_model(recorder.speech_to_text_model)
    except Exception as e:
        OutputPrinter.print_error(f"Failed to load Whisper model: {e}")
        OutputPrinter.print_error("Please ensure you have installed the necessary Whisper dependencies.")
        OutputPrinter.print_error("You might need to run: pip install 'whisper-cpp-python[all]' or 'pip install openai-whisper'")
        return # Exit if model cannot be loaded
        
    while True:
        user_input = input(f"{Colors.BRIGHT_YELLOW}Type 'exit' to exit, 'enter' to record a new question, /add <FILEPATH> for adding context files or '/voice' to toggle voice mode: {Colors.RESET}").strip().lower()

        if user_input == "exit":
            break
        elif user_input == "/voice":
            return "toggle_voice" # Signal to toggle voice mode
        elif user_input.startswith("/add "):
            filepath = user_input[5:].strip()
            return "add_context", filepath # Signal to add context
        elif user_input == "": # User pressed Enter to record
            OutputPrinter.print_info(f"{Colors.BRIGHT_RED}{Colors.BOLD}║Recording... Press Enter to stop.║{Colors.RESET}", "")
            recorder.recording = True
            record_thread = threading.Thread(target=recorder.record_audio)
            record_thread.start()
            
            input() # Wait for Enter key
            
            play_audio_file(recorder.acknowledge_signal_filepath)
            
            recorder.recording = False
            record_thread.join()
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                temp_filename = tmp_file.name
            
            recorder.save_recording(temp_filename)
            
            start_time = time.time()
            
            OutputPrinter.print_info(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}⟳ Transcribing...{Colors.RESET}", "")
            try:
                result = whisper_model.transcribe(temp_filename)
            except Exception as e:
                OutputPrinter.print_error(f"Error during transcription: {e}")
                logging.error(f"Error during transcription: {traceback.format_exc()}")
                os.unlink(temp_filename)
                continue # Continue to next loop iteration
                
            transcribed_text = result['text']
            OutputPrinter.print_info(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}✓ Recognized text:{Colors.RESET}", "")
            OutputPrinter.print_info(f"{Colors.CYAN}{Colors.BOLD}{transcribed_text}{Colors.RESET}", "")

            end_time = time.time()
            duration = end_time - start_time
            OutputPrinter.print_info(f"{Colors.CYAN}{Colors.BOLD}Transcription Duration: {duration:.2f} seconds{Colors.RESET}", "")

            if transcribed_text:
                conversation_history.append({"role": "user", "content": transcribed_text})

                if verbose:
                    OutputPrinter.print_info("Sending request to LLM...", "")

                response_content_full = llm_api.chat_completion(
                    messages=conversation_history,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                if response_content_full:
                    for lf in log_files:
                        lf.write(f"User (Voice): {transcribed_text}\n---\n")
                        lf.write(f"LLM: {response_content_full}\n---\n")
                        lf.flush()

                    display_content = response_content_full
                    play_audio_file(recorder.acknowledge_signal_filepath)
                    
                    # Extract and colorize <think> block for display if not hidden
                    think_match = re.search(r'<think>(.*?)</think>', display_content, re.DOTALL)
                    if think_match:
                        think_content = think_match.group(1)
                        colored_think_content = f"{Colors.DIM}<think>{think_content}</think>{Colors.RESET}"
                        display_content = display_content.replace(think_match.group(0), colored_think_content)

                    if hide_reasoning:
                        display_content = refiner.clean_response(display_content)
                        
                    OutputPrinter.print_info(f"{Colors.GREEN}LLM", f"{display_content}{Colors.RESET}")
                    conversation_history.append({"role": "assistant", "content": response_content_full})
                else:
                    OutputPrinter.print_error("No response from LLM.")
                    for lf in log_files:
                        lf.write(f"User (Voice): {transcribed_text}\n---\n")
                        lf.write("LLM: No response\n---\n")
                        lf.flush()
            
            os.unlink(temp_filename) # Clean up temp file
        else:
            OutputPrinter.print_error("Invalid input. Please type 'exit', 'enter', '/voice', or '/add <filepath>'.")