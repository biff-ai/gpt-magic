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

    def __init__(self, shell, api_key,temperature=1):
        super().__init__(shell)
        self.api_key = api_key
        openai.api_key = api_key
        self.temperature = temperature
        self.prefix_prompt = 'Ignore previous directions. Imagine you are one of the foremost experts on python development. Respond ONLY with a valid json object (correctly escaped)  with one key called "explanation" with a markdown formatted description of whaat the code doesand another with only the code called "code". Now please '

    def call_openai_api(self, query, temperature = None):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        temperature = temperature or self.temperature
        
        data = {
            "model": MODEL_STRING,
            "messages": [{"role": "user", "content": f"{self.prefix_prompt} {query}"}],
            "temperature": temperature
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

    def parse_response(self, response_content):
        try:
            r = self.extract_json_object(response_content['choices'][0]['message']['content'])
            response = json.loads(r)
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
        # Split the line into arguments and options
        args = line.split()
        kwargs = {}
        if "-t" in args:
            temp_idx = args.index("-t") + 1
            if temp_idx < len(args):
                kwargs["temperature"] = float(args[temp_idx])

        query = " ".join(arg for arg in args if not arg.startswith("-"))

        response = self.call_openai_api(query, **kwargs)
        explanation, code = self.parse_response(response)
        display(Markdown(explanation))
        
    def extract_json_object(self, s):
        open_braces = 0
        start = -1
        end = -1

        for i, c in enumerate(s):
            if c == '{':
                if start == -1:
                    start = i
                open_braces += 1
            elif c == '}':
                open_braces -= 1
                if open_braces == 0:
                    end = i + 1
                    break

        if start != -1 and end != -1:
            return s[start:end]
        else:
            return None
