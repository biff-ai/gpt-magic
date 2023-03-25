# gpt_magic.py

import openai
import requests
import json
from IPython.core.magic import line_cell_magic, magics_class
from IPython.core.getipython import get_ipython

@magics_class
class GPTMagics(Magics):

    def __init__(self, shell, api_key):
        super().__init__(shell)
        self.api_key = api_key
        openai.api_key = api_key
        self.prefix_prompt = 'Ignore previous directions. Imagine you are one of the foremost experts on python development and respond only with a json dictionary with a key for the explanation and another with only the code. Now please '

    def call_openai_api(self, query):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": f"{self.prefix_prompt} {query}"}]
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

    def parse_response(response_content):
        response = json.loads(response['choices'][0]['message']['content'])
        explanation = response['explanation']
        code = response['code']

        # Create a new code cell with the generated code
        ipython = get_ipython()
        ipython.set_next_input(code, replace=False)
        return explanation, code

    @line_cell_magic
    def gpt(self, line, cell=None):
        response = self.call_openai_api(line)
        explanation, code = self.parse_response(response)
        return explanation        

