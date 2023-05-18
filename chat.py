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
from typing import List, Iterator
# import speech_recognition as sr
import time
import sys
import io

# try:
#     import whisper
#     WHISPER_MODEL = whisper.load_model("base")
# except:
#     pass

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
    companies=", ".join(config.INTERVIEWER_COMPANIES),
    problem=config.EXAMPLE_PROBLEM
)

messages = [
    {
        "role": "system",
        "content": system_prompt
    }
]

#%%
def play_stream(audio):
    # test if audio is iterable
    if isinstance(audio, bytes):
        play(audio)
    else:
        stream(audio)

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

def transcribe(audio, state="", timeout=5):
    time.sleep(timeout)
    audio_file = open(audio, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    text = transcript["text"]
    state += text + " "
    return state, state

# def transcribe2(audio, state="", timeout=5, model=WHISPER_MODEL):
#     time.sleep(timeout)
#     # create a recognizer
#     audio = whisper.load_audio(audio)
#     audio = whisper.pad_or_trim(audio)
#     mel = whisper.log_mel_spectrogram(audio).to(model.device)
#     options = whisper.DecodingOptions(language= 'en', fp16=False)

#     result = whisper.decode(model, mel, options)
#     text = result.text
#     if result.no_speech_prob < 0.5:
#         print(result.text)
#         state += text + " "
#     return state, state

def user(user_message, history):
    return "", history + [[user_message, None]]

def tts(history, voice=INTERVIEWER_VOICE):
    text = history[-1][1]
    if text is None:
        return False
    text = text.replace("\n", " ")
    if text == "":
        return False
    audio = generate(
        text=text,
        voice=voice,
        model='eleven_monolingual_v1',
        stream=False,
    )
    play(audio)
    return True
    
def chat(history: List[List[str]]):
    global messages
    user_message = history[-1][0]
    messages.append({"role": "user", "content": user_message})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )

    response_message = response["choices"][0]["message"]
    print(response_message)
    messages.append(response_message)

    response_text = response_message["content"]
    
    # text to speech request with eleven labs
    # audio = generate(
    #     text=response_text.replace("\n", " "),
    #     voice=INTERVIEWER_VOICE,
    #     model='eleven_monolingual_v1',
    #     stream=True,
    # )
    # stream(audio)

    history[-1][1] = response_text
    return history#, output_filename
    
def bot(history):
    response_text = history[-1][1]
    history[-1][1] = ""
    for chunk in response_text:
        history[-1][1] += chunk
        # time.sleep(0.05)
        yield history

# def listen():
#     import speech_recognition as sr
#     r = sr.Recognizer()
#     with sr.Microphone() as source:
#         print('Calibrating...')
#         r.adjust_for_ambient_noise(source, duration=5)
#         # optional parameters to adjust microphone sensitivity
#         # r.energy_threshold = 200
#         # r.pause_threshold=0.5    
        
#         print('Okay, go!')
#         text = ''
#         print('listening now...')
#         try:
#             audio = r.listen(source, timeout=5, phrase_time_limit=30)
#             print('Recognizing...')
#             # whisper model options are found here: https://github.com/openai/whisper#available-models-and-languages
#             # other speech recognition models are also available.
#             text = r.recognize_whisper(audio, model='medium.en', show_dict=True, )['text']
#         except Exception as e:
#             unrecognized_speech_text = f'Sorry, I didn\'t catch that. Exception was: {e}s'
#             text = unrecognized_speech_text
#         print(text)
#     return text
#%%
fn_tests = config.EXAMPLE_TESTS
fn_soln = config.EXAMPLE_SOLUTION
# print(fn_soln + fn_tests)

def run_tests(fn_str, fn_tests=fn_tests):
    global_namespace = globals()
    local_namespace = {}
    exec(fn_str, global_namespace, local_namespace)
    global_namespace.update(local_namespace)
    old_stdout = sys.stdout
    sys.stdout = captured_stdout = io.StringIO()
    exec(fn_tests, global_namespace)
    sys.stdout = old_stdout
    output = captured_stdout.getvalue()
    print(output)
    return output

def run_code(fn_str):
    """ Run code in Code Box and update global namespace with variables defined in code """
    global_namespace = globals()
    local_namespace = {}
    old_stdout = sys.stdout
    sys.stdout = captured_stdout = io.StringIO()
    exec(fn_str, global_namespace, local_namespace)
    sys.stdout = old_stdout
    global_namespace.update(local_namespace)
    output = captured_stdout.getvalue()
    return output

# set a custom theme
theme = gr.themes.Default().set(
    body_background_fill="#000000",
)
css = """
#code-block {
    font-family: 'Consolas', Consolas, monospace;
    # padding: 10px;
    # border: 1px solid #ddd;
    # border-radius: 5px;
    # background-color: #f5f5f5;
}
"""
# code_default = config.EXAMPLE_SOLUTION
code_default = config.EXAMPLE_CODE_DEFAULT

with gr.Blocks(theme=theme) as demo:
    with gr.Row().style(css={'background-color': 'black'}):
        # interviewer image input and microphone input
        interviewer = gr.Image(value=config.INTERVIEWER_IMAGE).style(
            width=config.INTERVIEWER_IMAGE_WIDTH,
            height=config.INTERVIEWER_IMAGE_HEIGHT,
            container=True,
        )
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Box():
                chatbot = gr.Chatbot([], elem_id="chatbot").style(height=250)
                audio = gr.Audio(source="microphone", type="filepath", streaming=True)
                audio_text = gr.Textbox(
                    show_label=False, 
                    placeholder="Click the microphone to start recording",
                    interactive=True
                ).style(container=False)
                submit_msg = gr.Button("Submit Message")
        with gr.Column(scale=1):
            with gr.Box():
                code_box = gr.Textbox(
                    value=code_default,
                    label="Code Box", 
                    lines=10,
                    elem_id="code-block",
                    interactive=True
                )
                run_code_btn = gr.Button("Run Code")
                submit_code_btn = gr.Button("Submit Code")
                code_output = gr.Textbox(
                    value="",
                    label="Code Output",
                    lines=1,
                    elem_id="code-block",
                    interactive=False
                )
    # audio = gr.Audio(source="microphone", type="filepath")#, streaming=True)
    # audio_text = gr.Textbox(label="Audio Transcript")
    # record_btn = gr.Button("Record")
    # record_btn.click(listen, [], [audio_text])
    # text transcript output and audio 
    # chatbot = gr.Chatbot([], elem_id="chatbot").style(height=250)
    audio_state = gr.State(value="")
    # audio.change(transcribe, [audio, audio_state], [audio_text, audio_state]).then(
    #     user, [audio_state, chatbot], [audio_state, chatbot]).then(
    #     chat, chatbot, chatbot).then(
    #         tts, chatbot)
    audio.stream(transcribe, [audio], [audio_text, audio_state])#.then(
        # user, [audio_text, chatbot], [audio_text, chatbot]).then(
        # chat, chatbot, chatbot).then(
        #     tts, chatbot)
    audio_text.submit(user, [audio_text, chatbot], [audio_text, chatbot]).then(
        chat, chatbot, chatbot).then(
            tts, chatbot)
    submit_msg.click(user, [audio_text, chatbot], [audio_text, chatbot]).then(
        chat, chatbot, chatbot).then(
            tts, chatbot)
    # btn = gr.Button("Run")
    # btn.click(user, [audio_state, chatbot], [audio_state, chatbot]).then(
    #     chat, chatbot, chatbot)#[chatbot, audio_output])
    clear = gr.Button("Clear")
    clear.click(lambda: [None, code_default, ""], None, [chatbot, code_box, code_output], queue=False)
    run_code_btn.click(run_code, code_box, code_output)
    submit_code_btn.click(run_tests, code_box, code_output)

# if __name__ == "__main__":
demo.queue()
demo.launch(debug=False, share=False, server_name="0.0.0.0")
