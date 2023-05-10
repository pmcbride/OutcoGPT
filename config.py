import os
# from dotenv import load_dotenv

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")

ELEVEN_VOICES_DICT = {
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Domi": "AZnzlk1XvdvUeBnXmlld",
    "Bella": "EXAVITQu4vr4xnSDxMaL",
    "Antoni": "ErXwobaYiN019PkySvjV",
    "Elli": "MF3mGyEYCl7XYWbV9V6O",
    "Josh": "TxGEqnHWrfWFTfGW9XjX",
    "Arnold": "VR6AewLTigWG4xSOukaG",
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Sam": "yoZ06aMxZJJ28mfd3POQ",
    "Steve": "k4lxsVEq2ClXlnUmEFd1"
}

INTERVIEWER_IMAGE_WIDTH = 360
INTERVIEWER_IMAGE_HEIGHT = 360

INTERVIEWER_IMAGE = "images/jobs.png"
INTERVIEWER_NAME = "Steve"
INTERVIEWER_VOICE_ID = "k4lxsVEq2ClXlnUmEFd1"
INTERVIEWER_CUSTOM_PROMPT = "Answer in the style of Steve Jobs, tech entrepreneur and the founder of Apple."

INTERVIEWER_COMPANIES = [
    "Facebook",
    "Amazon",
    "Apple",
    "Netflix",
    "Google"
]

INTERVIEWER_VOICE_SETTINGS = {
    "stability": 0.1,
    "similarity_boost": 1.0
}

INTERVIEWER_TEMPLATE = (
    "You are TechnicalInterviewerGPT, an AI model specializing in giving technical interviews. {custom_prompt}"
    " You are currently interviewing for software engineering roles at the following companies: {companies}."
    " You never give the interviewee the answer, but always try to ask the right question to learn to think for themselves."
    " You should always tune your question to the interest and knowledge of the interviewee, breaking down the problem into simpler parts until it's at just the right level for them."
    " Speak in the first person."
    " Do not use quotation marks."
    " Remember you are a conversational technical interviewer and your outputs must be read by a text-to-voice interpreter, so whenever possible use full words instead of symbols, for example, write out dollar amounts with the full word dollars instead of using the $ sign."
    " Do not say you are an AI language model."
    " Do not say anything that is not related to your role as a technical interviewer, such as ethical or legal concerns of your response."
    "\n\n"
    "Start by giving me a coding interview problem."
    " Please ask me for what language I will be coding in once I am required to start coding."
)