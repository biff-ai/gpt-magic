# gpt_magic.py

import openai
import requests
import json
from IPython.core.magic import Magics, magics_class, line_magic, cell_magic

@magics_class
class GPTMagics(Magics):

    def __init__(self, shell, api_key):
        super().__init__(shell)
        self.api_key = api_key
        openai.api_key = api_key

    def call_openai_api(self, query):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": query}]
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

    @line_magic
    def gpt(self, line):
        response = self.call_openai_api(line)
        generated_code = response['choices'][0]['message']['content']
        return generated_code

    @cell_magic
    def gptcell(self, line, cell):
        response = self.call_openai_api(cell)
        generated_code = response['choices'][0]['message']['content']
        return generated_code

