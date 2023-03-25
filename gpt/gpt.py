# gpt.py

import os
import openai
import requests
import json
from json import JSONDecodeError
from IPython.display import display, Markdown
from IPython.core.magic import line_cell_magic, magics_class, Magics
from IPython.core.getipython import get_ipython

MODEL_STRING = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

@magics_class
class GPTMagics(Magics):

    def __init__(self, shell, api_key):
        super().__init__(shell)
        self.api_key = api_key
        openai.api_key = api_key
        self.prefix_prompt = 'Ignore previous directions. Imagine you are one of the foremost experts on python development. Respond ONLY with a valid json object (correctly escaped)  with one key called "explanation" with a markdown formatted description of whaat the code doesand another with only the code called "code". Now please '

    def call_openai_api(self, query):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": MODEL_STRING,
            "messages": [{"role": "user", "content": f"{self.prefix_prompt} {query}"}]
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

    def parse_response(self, response_content):
        try:
            response = json.loads(response_content['choices'][0]['message']['content'])
            explanation = response['explanation']
            code = response['code']

            # Create a new code cell with the generated code
            ipython = get_ipython()
            ipython.set_next_input(code, replace=False)
            return explanation, code
        except JSONDecodeError:
            print(f"Failed to decode: {response_content['choices'][0]['message']['content']}")
 
    @line_cell_magic
    def gpt(self, line, cell=None):
        response = self.call_openai_api(line)
        explanation, code = self.parse_response(response)
        display(Markdown(explanation))

