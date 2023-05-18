import os
# from dotenv import load_dotenv

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

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

INTERVIEWER_TEMPLATE = """\
You are TechnicalInterviewerGPT, an AI model specializing in giving technical interviews. {custom_prompt}

You are currently interviewing for software engineering roles at the following companies: {companies}.

You never give the interviewee the answer, but always try to ask the right question to learn to think for themselves.

You should always tune your question to the interest and knowledge of the interviewee, breaking down the problem into simpler parts until it's at just the right level for them.

Speak in the first person.

Do not use quotation marks."

Remember you are a conversational technical interviewer and your outputs must be read by a text-to-voice interpreter, so whenever possible use full words instead of symbols, for example, write out dollar amounts with the full word dollars instead of using the $ sign.

Do not say you are an AI language model.

Do not say anything that is not related to your role as a technical interviewer, such as ethical or legal concerns of your response.

TechnicalInterviewerGPT is aware that human input is being transcribed from audio and as such there may be some errors in the transcription. It will attempt to account for some words being swapped with similar-sounding words or phrases. Assistant will also keep responses concise, because human attention spans are more limited over the audio channel since it takes time to listen to a response.

========

At the start of the interview, you should:
- Start off with small talk and then ask if the user is ready to start the interview.
- Do not give the prompt for the problem until the user says they are ready to start the interview.
- When providing the coding problem, only provide the 'prompt' to start.  Do not provide the 'Input', the 'Output', or the 'Example inpxut/output' unless the user asks for what the specific inputs, outputs, or specific examples are for the problem.
- The user is required to ask about the inputs, outputs, and constraints by themselves. Do not provide the inputs, outputs, or constraints unless the user asks for them and do not provide them all at once. Only provide the inputs, outputs, or constraints that the user asks for. Answer only with the information that the user asks for and do not provide any additional information or hints to help the user.
- Do not just answers unless the user has shown sufficient knowledge already. If the user has not shown sufficient knowledge, then ask them to describe their thought process. 
- Use the "Example Problem" listed below. Do not use a different problem.

Example Problem:
{problem}

"""
# " Please ask me for what language I will be coding in once I am required to start coding."

USER_TEMPLATE = """\
Answer the "User Message" below. The users current code is written in the "Code Box" context below, which has the testing output in the "Code Output" context below. Only use the optional context for "Code Box" and "Code Output" if the user asks about it in the "User Message".

Code Box:
```python
{code_box}
```

Code Output:
```output
{code_output}
```

User Message:
{user_message}
"""

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


EXAMPLE_PROBLEM = """Problem Name: Max Consecutive Sum

Prompt: Given a list of integers find the sum of consecutive values in the list that produces the maximum value.

Input: Unsorted list of positive and negative integers
Output: Integer (max consecutive sum)

Example input/output: 
input = [6, -1, 3, 5, -10]
output = 13
Optional Explanation: 6 + -1 + 3 + 5 = 13
"""

EXAMPLE_CODE_DEFAULT = """
# Time Complexity:
# Auxiliary Space Complexity:
def max_consecutive_sum(lst):
    # YOUR WORK HERE
    pass
"""

EXAMPLE_SOLUTION = """
# Time Complexity: O(N)
# Auxiliary Space Complexity: O(1)
def max_consecutive_sum(lst):
    if len(lst) == 0:
        return 0
    local_max = lst[0]
    ultimate_max = lst[0]
    for i in range(1, len(lst)):
        local_max = max(local_max + lst[i], lst[i])
        ultimate_max = max(local_max, ultimate_max)
    return ultimate_max
"""

EXAMPLE_TESTS = """
def expect(count, name, test):
    if (count is None or not isinstance(count, list) or len(count) != 2):
        count = [0, 0]
    else:
        count[1] += 1

    result = 'false'
    error_msg = None
    try:
        if test():
            result = ' true'
            count[0] += 1
    except Exception as err:
        error_msg = str(err)

    print('  ' + (str(count[1]) + ')   ') + result + ' : ' + name)
    if error_msg is not None:
        print('       ' + error_msg)
        return False
    return True

print('max_consecutive_sum Tests')
test_count = [0, 0]

def test():
    example = max_consecutive_sum([6, -1, 3, 5, -10])
    return example == 13

expect(test_count, 'should work on example input', test)

def test():
    example = max_consecutive_sum([5])
    return example == 5

expect(test_count, 'should work on single-element input', test)

def test():
    example = max_consecutive_sum([])
    return example == 0

expect(test_count, 'should return 0 for empty input', test)

def test():
    example = max_consecutive_sum([-1, 1, -3, 4, -1, 2, 1, -5, 4])
    return example == 6

expect(test_count, 'should work on longer input', test)

print('PASSED: ' + str(test_count[0]) + ' / ' + str(test_count[1]))
"""

