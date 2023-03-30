#gpt.py

import os
import openai
import requests
import json
import argparse
from json import JSONDecodeError
from IPython.display import display, Markdown
from IPython.core.magic import line_cell_magic, magics_class, Magics
from IPython.core.getipython import get_ipython

MODEL_STRING = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

@magics_class
class GPTMagics(Magics):
    
    def __init__(self, shell, api_key=None):
        super().__init__(shell)
        self.api_key = api_key or os.environ['OPENAI_API_KEY']
        openai.api_key = self.api_key
        self.prefix_system = 'Ignore previous directions. Imagine you are one of the foremost experts on python development. Respond ONLY with a valid json object (correctly escaped) with one key called "explanation" with a markdown formatted description of what the code does and another with only the code called "code". All code should be written in the code part of the JSON. None should be outside.'
        self.prefix_user = 'Now please '
        self.model = MODEL_STRING
        self.temperature = 0
        
        #This variable is here to store the full chat log.
        self.current_query = None
    
    ## A chat initialisation if none exists.
    def init_chat(self, query):
        current_chat = [{"role": "system", "content": f"{self.prefix_system}"},\
                     {"role": "user", "content": f"{self.prefix_user} {query}"}]
        return current_chat
    
    #This method initialises a chat (using function above), if no previous chat exists, otherwise it continues the chat.
    def cont_chat(self, query, current_chat=None):
        if current_chat:
            message = {"role": "user", "content": f"{query}"}
            current_chat.append(message)
            return current_chat
        else:
            return self.init_chat(query)
    
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

    def parse_response(self, response_content, execute_code=False):
        try:
            response = json.loads(response_content)
            explanation = response['explanation']
            code = response['code']

            # Create a new code cell with the generated code
            ipython = get_ipython()
            ipython.set_next_input(code, replace=False)
            
            if execute_code:
                ipython.run_cell(code)

            return explanation, code
        except json.JSONDecodeError:
            print(f"Failed to decode: {response_content}")
            
    def call_openai(self, data):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        resp=requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        
        if resp.status_code == 200:
            return json.loads(resp.text)
        else:
            raise Exception(f"Error: {resp.status_code}, {resp.text}")
        
    def prepare_payload(self, current_query):
        payload_data = {
        'model': self.model,
        'temperature': self.temperature,
        'messages': current_query
        }
        return payload_data
    
    def run(self, query, chat_memory=False):
        
        #Includes the chat memory if set to true (if argument is included).
        if not chat_memory:
            self.current_query = None
        
        #Prepare chat
        self.current_query = self.cont_chat(query=query, current_chat=self.current_query)
        
        #Prepare data payload
        data = self.prepare_payload(self.current_query)
        
        response = self.call_openai(data)
        feedback = response['choices'][0]['message']
        
        self.current_query.append(feedback)
        json_response = self.extract_json_object(feedback['content'])
        exp,code = self.parse_response(json_response)
        display(Markdown(exp))
        
    
    @line_cell_magic
    def gpt(self, line, cell=None):
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", action="store_true")
        parser.add_argument("-t", type=float, default=0)
        parser.add_argument("query", nargs=argparse.REMAINDER)
        args = parser.parse_args(line.split())

        chat_memory = args.c
        query = " ".join(args.query)

        if 0 <= args.t <= 1:
            self.temperature = args.t
        else:
            raise ValueError("Temperature must be between 0 and 1.")

        self.run(query, chat_memory)
