import pytest
from IPython.testing.globalipapp import start_ipython
from dotenv import load_dotenv
import os
from gpt import GPTMagics

# Specify the path to the .env file
env_file_path = ".env"

# Load the .env file from the specified directory
load_dotenv(dotenv_path=env_file_path)

#Fixture to create an Ipython instance
@pytest.fixture(scope='session')
def session_ip():
    yield start_ipython()

#Fixture to unload and reload for a fresh instance.
@pytest.fixture(scope='function')
def ip(session_ip):
    session_ip.run_line_magic(magic_name='load_ext', line='gpt')
    yield session_ip
    session_ip.run_line_magic(magic_name='unload_ext', line='gpt')
    session_ip.run_line_magic(magic_name='reset', line='-f')

@pytest.fixture()
def gpt_magic(ip):
    api_key=os.environ['OPENAI_API_KEY']
    yield GPTMagics(ip)

@pytest.fixture()
def array_query():
    return 'please write a query that calculates the average from an array'

@pytest.fixture()
def initial_chatlog(gpt_magic, array_query):
    return gpt_magic.init_chat(array_query)

@pytest.fixture()
def initial_payload(gpt_magic, initial_chatlog):
    return gpt_magic.prepare_payload(initial_chatlog)

@pytest.fixture()
def initial_response():
    return {"id": "chatcmpl-6zpVMsALkjdIDqULgEX2aj29ZjSpI", "object": "chat.completion", "created": 1680194012, "model": "gpt-3.5-turbo-0301", "usage": {"prompt_tokens": 101, "completion_tokens": 238, "total_tokens": 339}, "choices": [{"message": {"role": "assistant", "content": "Sure, here's a JSON object with the requested information:\n\n```json\n{\n  \"explanation\": \"This code calculates the average value from an array of numbers. It first sums up all the numbers in the array using the `reduce` method, and then divides the sum by the length of the array to get the average.\",\n  \"code\": \"const arr = [1, 2, 3, 4, 5];\\nconst sum = arr.reduce((acc, val) => acc + val, 0);\\nconst avg = sum / arr.length;\\nconsole.log(avg);\"\n}\n``` \n\nAnd here's an example query that calculates the average of an array of numbers in JavaScript:\n\n```javascript\nconst arr = [1, 2, 3, 4, 5];\nconst sum = arr.reduce((acc, val) => acc + val, 0);\nconst avg = sum / arr.length;\nconsole.log(avg);\n``` \n\nThis code logs the average value of the array to the console, which in this case is `3`. You can replace the `arr` variable with any array of numbers to calculate its average."}, "finish_reason": "stop", "index": 0}]}