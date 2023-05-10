import os
# from dotenv import load_dotenv

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_LABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

ELEVEN_LABS_VOICES_DICT = {
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

ADVISOR_IMAGE_WIDTH = 360
ADVISOR_IMAGE_HEIGHT = 360

ADVISOR_IMAGE = "images/jobs.png"
ADVISOR_NAME = "Steve"
ADVISOR_VOICE_ID = "k4lxsVEq2ClXlnUmEFd1"
ADVISOR_CUSTOM_PROMPT = "Answer in the style of Steve Jobs, tech entrepreneur and the founder of Apple."

ADVISOR_COMPANIES = [
    "Facebook",
    "Amazon",
    "Apple",
    "Netflix",
    "Google"
]

ADVISOR_VOICE_SETTINGS = {
    "stability": 0.1,
    "similarity_boost": 1.0
}
