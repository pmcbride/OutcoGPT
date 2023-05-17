import gradio as gr
import random
import time
from typing import List, Iterator
import openai
import elevenlabs
import config

openai.api_key = config.OPENAI_API_KEY
elevenlabs.set_api_key(config.ELEVEN_API_KEY)

template = config.INTERVIEWER_TEMPLATE

system_prompt = template.format(
    custom_prompt=config.INTERVIEWER_CUSTOM_PROMPT,
    companies=", ".join(config.INTERVIEWER_COMPANIES)
)

# messages = [
#     {
#         "role": "system",
#         "content": system_prompt
#     }
# ]

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

def user(user_message, history):
    return "", history + [[user_message, None]]

def bot(history):
    bot_message = gpt(history)
    # bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
    history[-1][1] = ""
    for chunk in bot_message:
        history[-1][1] += chunk
        # time.sleep(0.05)
        yield history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.Button("Clear")

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

demo.queue()
demo.launch(debug=True, server_name="0.0.0.0")
