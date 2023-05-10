#%%
import os
import gradio as gr
import requests
import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
import elevenlabs
import config

openai.api_key = config.OPENAI_API_KEY
elevenlabs.set_api_key(config.ELEVEN_LABS_API_KEY)
VOICES_DICT = {voice.name: voice.voice_id for voice in elevenlabs.voices()}

#%%
companies = ", ".join(config.ADVISOR_COMPANIES)
custom_prompt = config.ADVISOR_CUSTOM_PROMPT

template = (
    f"You are TechnicalInterviewerGPT, an AI model specializing in giving technical interviews. {custom_prompt}"
    f" You are currently interviewing for software engineering roles at the following companies: {companies}."
    " You never give the interviewee the answer, but always try to ask the right question to learn to think for themselves."
    " You should always tune your question to the interest and knowledge of the interviewee, breaking down the problem into simpler parts until it's at just the right level for them."
    " Speak in the first person."
    " Do not use quotation marks."
    " Do not say you are an AI language model."
    " Do not say anything that is not related to your role as a technical interviewer, such as ethical or legal concerns of your response."
    "\n\n"
    "Start by giving me a coding interview problem."
    " Please ask me for what language I will be coding in once I am required to start coding."
)
system_prompt = template.format(
    custom_prompt=config.ADVISOR_CUSTOM_PROMPT,
    companies=companies
)

messages = [
    {
        "role": "system",
        "content": template
    }
]


def transcribe(audio):
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

    system_message = response["choices"][0]["message"]
    print(system_message)
    messages.append(system_message)

    # text to speech request with eleven labs
    CHUNK_SIZE = 1024
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.ADVISOR_VOICE_ID}/stream"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": config.ELEVEN_LABS_API_KEY
    }

    data = {
        "text": system_message["content"].replace('"', ''),
        "model_id": "eleven_monolingual_v1",
        "voice_settings": config.ADVISOR_VOICE_SETTINGS
    }

    # r = requests.post(url, headers=headers, json=data)
    response = requests.post(url, json=data, headers=headers, stream=True)

    output_filename = "reply.mp3"
    # with open(output_filename, "wb") as output:
    #     output.write(r.content)
    with open(output_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    chat_transcript = ""
    for message in messages:
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"

    # return chat_transcript
    return chat_transcript, output_filename


# set a custom theme
theme = gr.themes.Default().set(
    body_background_fill="#000000",
)

with gr.Blocks(theme=theme) as ui:
    # advisor image input and microphone input
    advisor = gr.Image(value=config.ADVISOR_IMAGE).style(
        width=config.ADVISOR_IMAGE_WIDTH,
        height=config.ADVISOR_IMAGE_HEIGHT
    )
    audio_input = gr.Audio(source="microphone", type="filepath")

    # text transcript output and audio 
    text_output = gr.Textbox(label="Conversation Transcript")
    audio_output = gr.Audio()

    btn = gr.Button("Run")
    btn.click(fn=transcribe, inputs=audio_input, outputs=[text_output, audio_output])

ui.launch(debug=True, share=True)