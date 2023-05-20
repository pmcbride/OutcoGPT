#%%
import multiprocessing
import time
from typing import List, Iterator
import elevenlabs
from elevenlabs import play, stream, generate, save
import openai
import config
import re
from bs4 import BeautifulSoup

openai.api_key = config.OPENAI_API_KEY
elevenlabs.set_api_key(config.ELEVEN_API_KEY)

INTERVIEWER_VOICE = elevenlabs.Voice(
    voice_id=config.INTERVIEWER_VOICE_ID,
    settings=config.INTERVIEWER_VOICE_SETTINGS
)

TEMPLATE = config.INTERVIEWER_TEMPLATE

SYSTEM_PROMPT = TEMPLATE.format(
    custom_prompt=config.INTERVIEWER_CUSTOM_PROMPT,
    companies=", ".join(config.INTERVIEWER_COMPANIES),
    problem=config.EXAMPLE_PROBLEM
)
file_idx = 0

def clean_text(text):
    text = re.sub(r'\n', ' ', text) # Replaces newlines with spaces
    text = re.sub(r'\r', '', text) # Removes carriage returns
    text = re.sub(r'\t', ' ', text) # Replaces tabs with spaces
    # text = re.sub(r'[^a-zA-Z0-9 ]', '', text) # Removes all non-alphanumeric characters excluding spaces
    return text

def clean_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    clean_text = soup.get_text(separator=' ')
    return clean_text

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
#%%
if __name__ == "__main__":
    sentence_queue = multiprocessing.Queue()
    audio_queue = multiprocessing.Queue()
    writer = multiprocessing.Process(target=tts_writer, args=(sentence_queue, audio_queue))
    playback = multiprocessing.Process(target=tts_playback, args=(audio_queue,))

    writer.start()
    playback.start()

    user_message = "Hello, how are you doing today?"
    history = [[user_message, None]]
    # assistant_message = "".join(gpt(history))

    assistant_message = ("Hello! I'm doing great, thank you for asking. "
                         "I hope you're doing well too. "
                         "Are you ready to start the technical interview?")
    print(assistant_message)
    current_sentence = ""
    for chunk in assistant_message:
        print(chunk, end="")
        current_sentence += chunk
        if chunk[-1] in ["\n", ".", "?"]:
            print(f"\n{current_sentence}")
            sentence_queue.put(current_sentence)
            current_sentence = ""  # Reset current_sentence after yielding
    
    # assistant_message = "Hello! I'm doing great, thank you for asking. "
    # sentence_queue.put(assistant_message)
    # assistant_message = "I hope you're doing well too. "
    # sentence_queue.put(assistant_message)
    # assistant_message = "Are you ready to start the technical interview?"
    # sentence_queue.put(assistant_message)

    writer.join()
    # audio_queue.put(None)  # Signal that we're done
    playback.join()

# %%
# user_message = "Hello, how are you doing today?"
# history = [[user_message, None]]
# assistant_message = "".join(gpt(history))
# # %%
# assistant_message
# # %%
