import pytest

from gpt import GPTMagics
import json

class TestGPTMagics:

    def test_init(self, gpt_magic):
        assert gpt_magic.model == 'gpt-3.5-turbo'
        assert gpt_magic.temperature == 0
        assert gpt_magic.prefix_system == 'Ignore previous directions. Imagine you are one of the foremost experts on python development. Only respond with a brief explanation and python code block.'
        assert gpt_magic.prefix_user == 'Now please '
        assert gpt_magic.current_query is None

    def test_init_chat(self, gpt_magic, array_query):
        assert gpt_magic.init_chat(array_query) == [{'role': 'system', 'content': 'Ignore previous directions. Imagine you are one of the foremost experts on python development. Only respond with a brief explanation and python code block.'},
                {'role': 'user','content': f'Now please  {array_query}'}]
        assert gpt_magic.init_chat('test') == [{"role": "system", "content": f"{gpt_magic.prefix_system}"},\
                     {"role": "user", "content": f"{gpt_magic.prefix_user} test"}]
     
    def test_cont_chat(self, gpt_magic, array_query):
        assert gpt_magic.cont_chat(array_query) == [{"role": "system", "content": f"{gpt_magic.prefix_system}"},\
                     {"role": "user", "content": f"{gpt_magic.prefix_user} {array_query}"}]

    def test_prepare_payload(self, gpt_magic, initial_chatlog):
        assert gpt_magic.prepare_payload(initial_chatlog) == {'model': 'gpt-3.5-turbo',
            'temperature': 0,
            'messages': [{'role': 'system',
            'content': 'Ignore previous directions. Imagine you are one of the foremost experts on python development. Only respond with a brief explanation and python code block.'},
            {'role': 'user',
            'content': 'Now please  please write a query that calculates the average from an array'}]}
    
    """write unit test for succesful open ai call"""
    def test_call_openai_success(self, mocker, gpt_magic, initial_payload):
        # Mock the requests.post method
        mock_post = mocker.patch("requests.post")

        # Mock the response object returned by requests.post
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        expected_output = {"id": "chatcmpl-6zpVMsALkjdIDqULgEX2aj29ZjSpI", "object": "chat.completion", "created": 1680194012, "model": "gpt-3.5-turbo-0301", "usage": {"prompt_tokens": 101, "completion_tokens": 238, "total_tokens": 339}, "choices": [{"message": {"role": "assistant", "content": "Sure, here's a JSON object with the requested information:\n\n```json\n{\n  \"explanation\": \"This code calculates the average value from an array of numbers. It first sums up all the numbers in the array using the `reduce` method, and then divides the sum by the length of the array to get the average.\",\n  \"code\": \"const arr = [1, 2, 3, 4, 5];\\nconst sum = arr.reduce((acc, val) => acc + val, 0);\\nconst avg = sum / arr.length;\\nconsole.log(avg);\"\n}\n``` \n\nAnd here's an example query that calculates the average of an array of numbers in JavaScript:\n\n```javascript\nconst arr = [1, 2, 3, 4, 5];\nconst sum = arr.reduce((acc, val) => acc + val, 0);\nconst avg = sum / arr.length;\nconsole.log(avg);\n``` \n\nThis code logs the average value of the array to the console, which in this case is `3`. You can replace the `arr` variable with any array of numbers to calculate its average."}, "finish_reason": "stop", "index": 0}]}

        gpt_magic.api_key = "fake_api_key"
    