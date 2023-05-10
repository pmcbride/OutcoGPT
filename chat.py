#%%
import os
import gradio as gr
import requests
import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
import elevenlabs
from elevenlabs import generate, play, save, stream
import elevenlabs as el
import subprocess
from collections.abc import Iterator

import config
from config import (
    INTERVIEWER_NAME,
    INTERVIEWER_VOICE_ID,
    INTERVIEWER_VOICE_SETTINGS,
)

openai.api_key = config.OPENAI_API_KEY
elevenlabs.set_api_key(config.ELEVEN_API_KEY)

INTERVIEWER_VOICE = elevenlabs.Voice(
    voice_id=config.INTERVIEWER_VOICE_ID,
    settings=config.INTERVIEWER_VOICE_SETTINGS
)

template = config.INTERVIEWER_TEMPLATE

system_prompt = template.format(
    custom_prompt=config.INTERVIEWER_CUSTOM_PROMPT,
    companies=", ".join(config.INTERVIEWER_COMPANIES)
)

messages = [
    {
        "role": "system",
        "content": system_prompt
    }
]

#%%
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
        
def chat(audio):
    global messages

    # API now requires an extension so we will rename the file
    audio_filename_with_extension = audio + '.wav'
    os.rename(audio, audio_filename_with_extension)

    audio_file = open(audio_filename_with_extension, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    user_text = transcript["text"]
    messages.append({"role": "user", "content": user_text})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )

    response_message = response["choices"][0]["message"]
    print(response_message)
    messages.append(response_message)

    response_text = response_message["content"]
    
    # text to speech request with eleven labs
    stream = True
    
    audio = generate(
        text=response_text.replace("\n", " "),
        voice=INTERVIEWER_VOICE,
        model='eleven_monolingual_v1',
        stream=stream,
    )

    if stream == True:
        output_filename = "reply_stream.mp3"
        stream_to_file(audio, output_filename)
    else:
        output_filename = "reply.mp3"
        play(audio)
        save(audio, output_filename)

    chat_transcript = ""
    for message in messages:
        if message["role"] != "system":
            chat_transcript += message["role"] + ": " + message["content"] + "\n\n"

    # chat_transcript = "".join([
    #     f'{message["role"]}: {message["content"]}\n\n"'
    #     for message in messages
    #     if message["role"] != "system"
    # ])
    
    
    # return chat_transcript
    return chat_transcript, output_filename

# set a custom theme
theme = gr.themes.Default().set(
    body_background_fill="#000000",
)

with gr.Blocks(theme=theme) as ui:
    # advisor image input and microphone input
    advisor = gr.Image(value=config.INTERVIEWER_IMAGE).style(
        width=config.INTERVIEWER_IMAGE_WIDTH,
        height=config.INTERVIEWER_IMAGE_HEIGHT
    )
    audio_input = gr.Audio(source="microphone", type="filepath")

    # text transcript output and audio 
    text_output = gr.Textbox(label="Conversation Transcript")
    audio_output = gr.Audio()

    btn = gr.Button("Run")
    btn.click(
        fn=chat, 
        inputs=audio_input, 
        # outputs=text_output
        outputs=[text_output, audio_output]
    )

ui.launch(debug=True, share=True)
# advisor = gr.Image(value=config.INTERVIEWER_IMAGE).style(width=config.INTERVIEWER_IMAGE_WIDTH, height=config.INTERVIEWER_IMAGE_HEIGHT)
# audio_input = gr.Audio(source="microphone", type="filepath")
# text_output = gr.Textbox(label="Conversation Transcript")
# audio_output = gr.Audio()
# ui = gr.Interface(fn=chat, inputs=audio_input, outputs=[text_output, audio_output])
# ui.launch(debug=True, share=True)