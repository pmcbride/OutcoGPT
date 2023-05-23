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
import multiprocessing


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

SYSTEM_PROMPT = template.format(
    custom_prompt=config.INTERVIEWER_CUSTOM_PROMPT,
    companies=", ".join(config.INTERVIEWER_COMPANIES),
    problem=config.EXAMPLE_PROBLEM
)

messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
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

import whisper
WHISPER_MODEL = whisper.load_model("base")
def transcribe2(audio, state="", timeout=5, model=WHISPER_MODEL):
    # time.sleep(timeout)
    # create a recognizer
    audio = whisper.load_audio(audio)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    options = whisper.DecodingOptions(language= 'en', fp16=False)

    result = whisper.decode(model, mel, options)
    text = result.text
    if result.no_speech_prob < 0.5:
        print(f"Text: {result.text}")
        state += text + " "
        print(f"State: {state}")
    return state, state
#%%
def user(user_message, code_box, history):
    if user_message == "":
        return "", "", history
    if ("code box" in user_message.lower()) or ("codebox" in user_message.lower()):
        user_message += f"\n\nCode Box:\n```python\n{code_box}\n```"
    return "", "", history + [[user_message, None]]

import re
def clean_text(text):
    text = re.sub(r'\n', ' ', text) # Replaces newlines with spaces
    text = re.sub(r'\r', '', text) # Removes carriage returns
    text = re.sub(r'\t', ' ', text) # Replaces tabs with spaces
    text = re.sub(r'=', ' equals ', text) # Replaces tabs with spaces
    text = re.sub(r'\[', ' ', text) # Replaces tabs with spaces
    text = re.sub(r'\]', ' ', text) # Replaces tabs with spaces
    text = re.sub(r' -', ' negative ', text) # Replaces tabs with spaces
    # text = re.sub(r'[^a-zA-Z0-9 ]', '', text) # Removes all non-alphanumeric characters excluding spaces
    return text

from bs4 import BeautifulSoup
def clean_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    clean_text = soup.get_text(separator=' ')
    return clean_text

wav_idx = 0
def tts(history, voice=INTERVIEWER_VOICE):
    global wav_idx
    original_string = text = history[-1][1]
    if text is None:
        return False
    text = clean_html(text)
    text = clean_text(text)
    if text == "":
        return False
    print(f"\ntts: {text}")
    audio = generate(
        text=text,
        voice=voice,
        model='eleven_monolingual_v1',
        stream=False,
    )
    audio_file = f"audio/audio_steve_{wav_idx:06d}.wav"
    audio_string = f'<audio src="file/{audio_file}" controls autoplay></audio>'
    save(audio, audio_file)
    wav_idx += 1
    history[-1][1] = f"{audio_string}\n\n{original_string}"
    return history, audio_file

def remove_autoplay(history):
    # Remove autoplay from the last reply
    new_history = []
    if len(history) > 0:
        for user_message, response in history:
            response = response.replace('controls autoplay>', 'controls>') if not None else response
            new_history.append([user_message, response])
    return new_history

def tts2(text, voice=INTERVIEWER_VOICE):
    if text is None:
        return False
    if text == "RETURN_CODE_BOX_CONTENTS":
        return False
    text = clean_text(clean_html(text))
    if text == "":
        return False
    print(f"\ntts: {text}")
    audio = generate(
        text=text,
        voice=voice,
        model='eleven_monolingual_v1',
        stream=False,
    )
    play(audio)
    return text

def gpt(history: List[List[str]]) -> Iterator[str]:
    # global messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for user_content, assistant_content in history:
        messages.append({"role": "user", "content": user_content})
        if assistant_content is not None:
            messages.append({"role": "assistant", "content": assistant_content})
        else:
            break

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        stream=True,
        temperature=0
    )
    for chunk in response:
        response_text = chunk['choices'][0]['delta'].get("content", None)
        if response_text is not None:
            print(f"gpt: {response_text}")#, end="")
            yield response_text

def tts_audio(text, voice=INTERVIEWER_VOICE):
    if text is None:
        return False
    if text == "RETURN_CODE_BOX_CONTENTS":
        return False
    text = clean_text(text)
    if text == "":
        return False
    print(f"\ntts: {text}")
    audio = generate(
        text=text,
        voice=voice,
        model='eleven_monolingual_v1',
        stream=False,
    )
    return audio

file_idx = 0
def tts_writer(sentence_queue, audio_queue):
    global file_idx
    while True:
        sentence = sentence_queue.get()
        if sentence_queue is None:  # This is a signal that we're done
            print("Sentence queue is None")
            continue
        print(f"\ntts_write: {sentence}")
        # with open(f"file_{file_idx}.txt", "w") as f:
        #     f.write(sentence)
        file_idx += 1
        audio = tts_audio(sentence) 
        audio_queue.put(audio)

def tts_playback(audio_queue):
    while True:
        audio = audio_queue.get()
        if audio is None:  # This is a signal that we're done
            continue
        play(audio)  # Implement this function

def bot(history):#, code_box):
    # global sentence_queue, audio_queue
    
    bot_message = gpt(history)
    history[-1][1] = ""
    current_sentence = ""
    for chunk in bot_message:
        history[-1][1] += chunk
        current_sentence += chunk
        sentence_length = len(current_sentence.split(" ")) # Sentence length in words
        # if chunk in ["\n", ".", "?", "!", ":", ";"]:#, ","]:
        for char in chunk:
            if char in ["\n", ".", "?", ":", ";"] or (char == "," and sentence_length > 3) or (char == "!" and sentence_length > 1):
                # sentence_queue.put(current_sentence)
                # tts2(current_sentence)
                current_sentence = ""  # Reset current_sentence after yielding
                break
        yield history #, history[-1][1]

    # After all chunks have been processed, if there is a remaining sentence, yield it too
    # if current_sentence:
    #     sentence_queue.put(current_sentence)
    #     yield history, history[-1][1]

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

    history[-1][1] = response_text
    return history#, output_filename

        
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
#image-block iframe {
    border: none
}
"""
# code_default = config.EXAMPLE_SOLUTION
code_default = config.EXAMPLE_CODE_DEFAULT

def get_code_feedback(code_box):
    user_message = config.CODE_FEEDBACK_TEMPLATE.format(code_box=code_box)
    return user_message

with gr.Blocks(theme=theme) as demo:
    with gr.Row().style(css={'background-color': 'black'}):
        # interviewer image input and microphone input
        interviewer = gr.Image(value=config.INTERVIEWER_IMAGE).style(
            width=config.INTERVIEWER_IMAGE_WIDTH,
            height=config.INTERVIEWER_IMAGE_HEIGHT,
            container=True,
            # elem_id="image-block"
        )
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Box():
                chatbot = gr.Chatbot([], elem_id="chatbot").style(height=500)
                audio = gr.Audio(source="microphone", type="filepath")#, streaming=True)
                audio_text = gr.Textbox(
                    show_label=False, 
                    placeholder="Click the microphone to start recording",
                    interactive=True
                ).style(container=False)
                submit_msg = gr.Button("Submit Message")
                audio_steve = gr.Audio(label="Steve", type="filepath")
        with gr.Column(scale=1):
            with gr.Box():
                code_box = gr.Textbox(
                    value=code_default,
                    label="Code Box", 
                    lines=20,
                    elem_id="code-block",
                    interactive=True
                )
                run_code_btn = gr.Button("Run Code")
                submit_code_btn = gr.Button("Submit Code")
                code_feedback_btn = gr.Button("Code Feedback")
                code_output = gr.Textbox(
                    value="",
                    label="Code Output",
                    lines=1,
                    elem_id="code-block",
                    interactive=False
                )
    current_sentence = gr.State(value="")
    audio_state = gr.State(value="")
    (audio.change(transcribe2, [audio, audio_state], [audio_text, audio_state])
    .then(lambda: None, None, audio)
    .then(remove_autoplay, chatbot, chatbot)
    .then(user, [audio_state, code_box, chatbot], [audio_text, audio_state, chatbot])
    .then(bot, chatbot, chatbot)  # Ensure bot function outputs current_sentence
    .then(tts, chatbot, [chatbot, audio_steve]) # Now current_sentence is an output from bot function
    # .then(tts2, current_sentence) # Now current_sentence is an output from bot function
    )
    # chatbot.change(remove_autoplay, chatbot, chatbot)
    (audio_text.submit(user, [audio_state, code_box, chatbot], [audio_text, audio_state, chatbot])
     .then(bot, chatbot, chatbot)
    #  .then(tts, chatbot)
     )
    (submit_msg.click(user, [audio_state, code_box, chatbot], [audio_text, audio_state, chatbot])
     .then(bot, chatbot, chatbot)
    #  .then(tts, chatbot)
     )
    # btn = gr.Button("Run")
    # btn.click(user, [audio_state, chatbot], [audio_state, chatbot]).then(
    #     chat, chatbot, chatbot)#[chatbot, audio_steve])
    clear = gr.Button("Clear")
    clear.click(lambda: [None, code_default, ""], None, [chatbot, code_box, code_output], queue=False)
    run_code_btn.click(run_code, code_box, code_output)
    submit_code_btn.click(run_tests, code_box, code_output)
    (code_feedback_btn.click(get_code_feedback, code_box, audio_state)
     .then(user, [audio_state, code_box, chatbot], [audio_text, audio_state, chatbot])
     .then(bot, chatbot, chatbot)
    #  .then(tts2, current_sentence)
     )

if __name__ == "__main__":
    # sentence_queue = multiprocessing.Queue()
    # audio_queue = multiprocessing.Queue()
    # writer = multiprocessing.Process(target=tts_writer, args=(sentence_queue, audio_queue))
    # playback = multiprocessing.Process(target=tts_playback, args=(audio_queue,))
    # writer.start()
    # playback.start()
    demo.queue(concurrency_count=16)
    demo.launch(debug=False, share=True, server_name="0.0.0.0", max_threads=16)
    # writer.join()
    # playback.join()
