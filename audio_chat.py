#%% Imports
import sys
import os
import io
import gradio as gr
import random
import time
from typing import List, Iterator
import openai
import elevenlabs
import config
from elevenlabs import generate, play, save, stream

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
print("system_prompt:")
print(system_prompt)
# messages = [
#     {
#         "role": "system",
#         "content": system_prompt
#     }
# ]
#%% Functions
def gpt(history: List[List[str]]) -> Iterator[str]:
    # global messages
    messages = [{"role": "system", "content": system_prompt}]
    for user_content, assistant_content in history:
        messages.append({"role": "user", "content": user_content})
        if assistant_content is not None:
            messages.append({"role": "assistant", "content": assistant_content})
        else:
            break
    # user_message = {"role": "user", "content": user_message}
    # print(user_message)
    
    # messages.append(user_message)

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        stream=True,
        temperature=0
    )
    for chunk in response:
        response_text = chunk['choices'][0]['delta'].get("content", None)
        if response_text is not None:
            print(response_text, end="")
            yield response_text
    # response_message = response["choices"][0]["message"]
    # print(response_message)
    # messages.append(response_message)

    # response_text = response_message["content"]
    # return response_text

def user(user_message, history):#, code_box, code_output):
    # user_message = config.USER_TEMPLATE.format(
    #     code_box=code_box, code_output=code_output, user_message=user_message)
    return "", history + [[user_message, None]]

def bot(history):
    bot_message = gpt(history)
    # bot_message = random.choice(["How are you?", "Hello! I'm Steve Jobs, and I'll be conducting your technical interview today. We'll be discussing a coding problem to assess your problem-solving skills and technical knowledge. Before we begin, which programming language would you prefer to use for this interview?"])
    history[-1][1] = ""
    for chunk in bot_message:
        history[-1][1] += chunk
        # time.sleep(0.05)
        yield history

def transcribe(audio, state=""):
    time.sleep(2)
    audio_file = open(audio, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    text = transcript["text"]
    state += text + " "
    return state, state

def tts(history, voice=INTERVIEWER_VOICE, stream=False):
    text = history[-1][1]
    audio = generate(
        text=text,
        voice=voice,
        model='eleven_monolingual_v1',
        stream=stream,
    )
    play(audio)
    return audio
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

# output = run_tests(fn_soln)
# print(output)

#%% Gradio

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

with gr.Blocks(theme=theme, css=css) as demo:
    with gr.Row():
        with gr.Column(scale=0.5):
            with gr.Box():
                chatbot = gr.Chatbot([], elem_id="chatbot").style(height=750)
                audio = gr.Audio(source="microphone", type="filepath")
                msg = gr.Textbox(
                    show_label=False, placeholder="Click the microphone to start recording"
                ).style(container=False)
                submit_msg = gr.Button("Submit Message")
        with gr.Column(scale=0.5):
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
    # Create a play button to run tts for the last chatbot message
    play_btn = gr.Button("Play")
    play_btn.click(tts, chatbot, gr.Audio())
    
    state = gr.State(value="")
    audio.stream(fn=transcribe, inputs=[audio, state], outputs=[msg, state], queue=False)#.then(
        # user, [msg, chatbot], [msg, chatbot])
    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(bot, chatbot, chatbot)#.then(tts, chatbot, gr.Audio())
    submit_msg.click(user, [msg, chatbot], [msg, chatbot], queue=False).then(bot, chatbot, chatbot)#.then(tts, chatbot, gr.Audio())
    # chatbot.change(tts, chatbot, gr.Audio())
    clear = gr.Button("Clear")
    clear.click(lambda: [None, code_default, ""], None, [chatbot, code_box, code_output], queue=False)
    run_code_btn.click(run_code, code_box, code_output)
    submit_code_btn.click(run_tests, code_box, code_output)

#%% Launch
# if __name__ == "__main__":
demo.queue()
demo.launch(debug=True, server_name="0.0.0.0")
