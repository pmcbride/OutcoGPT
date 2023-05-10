import os
# from dotenv import load_dotenv

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
ELEVEN_LABS_VOICE_ID=os.getenv("ELEVEN_LABS_VOICE_ID")

ADVISOR_IMAGE_WIDTH = 360
ADVISOR_IMAGE_HEIGHT = 360

ADVISOR_IMAGE = "images/jobs.png"
ADVISOR_VOICE_ID = ELEVEN_LABS_VOICE_ID or "voice_id_from_eleven_labs_here"
ADVISOR_CUSTOM_PROMPT = "Answer in the style of Steve Jobs, tech entrepreneur and the founder of Apple."

COMPANIES = ["Facebook", "Amazon", "Apple", "Netflix", "Google"]

