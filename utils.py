
from collections.abc import Iterator
import subprocess
import elevenlabs
from elevenlabs import generate, play, save, stream

def get_voice(voice, voice_settings=config.INTERVIEWER_VOICE_SETTINGS):
    if isinstance(voice, str):
        voice_str = voice
        # If voice is valid voice_id, use it
        if el.is_voice_id(voice):
            voice = el.Voice(voice_id=voice)
        # Otherwise, search voice by name
        else:
            # If not, query API
            print(f"Searching for '{voice}'...")
            voice = next((v for v in el.voices() if v.name == voice), None)  # type: ignore # noqa E501
        # Raise error if voice not found
        if not voice:
            raise ValueError(f"Voice '{voice_str}' not found.")
    # voice = next((v for v in el.voices() if v.name == name), None)
    voice.settings = el.VoiceSettings(**voice_settings)
    return voice

def get_voices_dict():
    return {voice.name: voice for voice in elevenlabs.voices()}

def stream_to_file(audio_stream: Iterator[bytes], filename: str = None) -> None:
    if not elevenlabs.is_installed("mpv"):
        raise ValueError("mpv not found, necessary to stream audio.")

    mpv_command = ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"]
    mpv_process = subprocess.Popen(
        mpv_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Open the file if a filename is provided
    file = open(filename, 'wb') if filename is not None else None

    for chunk in audio_stream:
        if chunk is not None:
            mpv_process.stdin.write(chunk)  # type: ignore
            mpv_process.stdin.flush()  # type: ignore

            # Write the chunk to the file as well if a file is open
            if file is not None:
                file.write(chunk)

    if mpv_process.stdin:
        mpv_process.stdin.close()
    mpv_process.wait()

    # Close the file if a file was open
    if file is not None:
        file.close()


def stream_save(audio_stream: Iterator[bytes], 
                filename: str = "audio_stream.mp3") -> None:
    if not elevenlabs.is_installed("mpv"):
        raise ValueError("mpv not found, necessary to stream audio.")

    mpv_command = ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"]
    mpv_process = subprocess.Popen(
        mpv_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    
    collected_chunks = []
    with open(filename, 'wb') as f:
        for chunk in audio_stream:
            if chunk is not None:
                mpv_process.stdin.write(chunk)  # type: ignore
                mpv_process.stdin.flush()  # type: ignore
                collected_chunks.append(chunk)
                f.write(chunk)

    if mpv_process.stdin:
        mpv_process.stdin.close()
    mpv_process.wait()

    full_stream = b"".join(collected_chunks)
    return full_stream
    
if __name__ == "__main__":
    audio_stream = generate(
        text="Hi! My name is Steve, nice to meet you!",
        voice=INTERVIEWER_VOICE,
        model='eleven_monolingual_v1',
        stream=True,
    )
    stream_save(audio_stream, "test_audio_stream.mp3")

